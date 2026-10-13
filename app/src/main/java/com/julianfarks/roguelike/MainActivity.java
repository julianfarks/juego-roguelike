package com.julianfarks.roguelike;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        TextView t = new TextView(this);
        t.setText("SwordmanRogue - pipeline OK");
        t.setTextSize(28);
        setContentView(t);
    }
}
