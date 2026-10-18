package pc;

import com.jcraft.jogg.Packet;
import com.jcraft.jogg.Page;
import com.jcraft.jogg.StreamState;
import com.jcraft.jogg.SyncState;
import com.jcraft.jorbis.Block;
import com.jcraft.jorbis.Comment;
import com.jcraft.jorbis.DspState;
import com.jcraft.jorbis.Info;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * Decodificador OGG Vorbis completo sobre JOrbis (como el ejemplo oficial DecodeExample). Existe porque el SPI de Java Sound
 * (vorbisspi) pierde los efectos muy cortos. Solo se compila cuando la libreria jorbis esta en el classpath (build.sh);
 * PcAudio lo busca por reflexion y, si no esta, usa el SPI.
 */
public final class OggJorbis {
    private OggJorbis() {}

    /** Devuelve {byte[] pcm16 little endian intercalado, Integer canales, Integer frecuencia}. */
    public static Object[] decode(InputStream in) throws Exception {
        SyncState oy = new SyncState();
        StreamState os = new StreamState();
        Page og = new Page();
        Packet op = new Packet();
        Info vi = new Info();
        Comment vc = new Comment();
        DspState vd = new DspState();
        Block vb = new Block(vd);
        ByteArrayOutputStream out = new ByteArrayOutputStream(1 << 16);
        oy.init();

        int index = oy.buffer(4096);
        int bytes = in.read(oy.data, index, 4096);
        if (bytes <= 0) throw new Exception("OGG vacio");
        oy.wrote(bytes);
        if (oy.pageout(og) != 1) throw new Exception("no es un OGG");
        os.init(og.serialno());
        vi.init();
        vc.init();
        if (os.pagein(og) < 0) throw new Exception("error leyendo la primera pagina");
        if (os.packetout(op) != 1) throw new Exception("error leyendo el primer paquete");
        if (vi.synthesis_headerin(vc, op) < 0) throw new Exception("no es Vorbis");

        int i = 0;
        while (i < 2) {
            while (i < 2) {
                int result = oy.pageout(og);
                if (result == 0) break;
                if (result == 1) {
                    os.pagein(og);
                    while (i < 2) {
                        result = os.packetout(op);
                        if (result == 0) break;
                        if (result == -1) throw new Exception("cabecera Vorbis corrupta");
                        vi.synthesis_headerin(vc, op);
                        i++;
                    }
                }
            }
            index = oy.buffer(4096);
            bytes = in.read(oy.data, index, 4096);
            if (bytes <= 0 && i < 2) throw new Exception("fin de archivo antes de las cabeceras");
            oy.wrote(Math.max(0, bytes));
        }

        int ch = vi.channels, rate = vi.rate;
        int convsize = 4096 / ch;
        byte[] conv = new byte[4096 * 2];
        vd.synthesis_init(vi);
        vb.init(vd);
        float[][][] pcmHolder = new float[1][][];
        int[] pcmIndex = new int[ch];

        boolean eos = false;
        while (!eos) {
            while (!eos) {
                int result = oy.pageout(og);
                if (result == 0) break;
                if (result != -1) {
                    os.pagein(og);
                    while (true) {
                        result = os.packetout(op);
                        if (result == 0) break;
                        if (result == -1) continue;
                        if (vb.synthesis(op) == 0) vd.synthesis_blockin(vb);
                        int samples;
                        while ((samples = vd.synthesis_pcmout(pcmHolder, pcmIndex)) > 0) {
                            float[][] pcm = pcmHolder[0];
                            int bout = Math.min(samples, convsize);
                            for (int c = 0; c < ch; c++) {
                                int ptr = c * 2;
                                int mono = pcmIndex[c];
                                for (int j = 0; j < bout; j++) {
                                    int val = (int) (pcm[c][mono + j] * 32767.0f);
                                    if (val > 32767) val = 32767;
                                    if (val < -32768) val = -32768;
                                    conv[ptr] = (byte) val;
                                    conv[ptr + 1] = (byte) (val >> 8);
                                    ptr += 2 * ch;
                                }
                            }
                            out.write(conv, 0, 2 * ch * bout);
                            vd.synthesis_read(bout);
                        }
                    }
                    if (og.eos() != 0) eos = true;
                }
            }
            if (!eos) {
                index = oy.buffer(4096);
                bytes = in.read(oy.data, index, 4096);
                if (bytes <= 0) eos = true; else oy.wrote(bytes);
            }
        }
        os.clear();
        vb.clear();
        vd.clear();
        vi.clear();
        oy.clear();
        return new Object[]{out.toByteArray(), ch, rate};
    }
}
