"""Reproduce geometry, matrix, number and mechanism fixtures from the Java baseline.

Usage: python tools/legacy_extended_probe.py /path/to/legacy > tests/fixtures/legacy-extended.json
Uses the same isolated, encoding-normalized compiler workflow as legacy_probe.py.
"""

import legacy_probe

legacy_probe.PROBE = r"""
import java.util.Vector;
import util.hypercomplex.*;
import util.hypercomplex.mechanism.*;
import util.basics.*;
import util.tinker.PolynominalGuess;
class LegacyProbe {
    static void show(String name, double... values) {
        System.out.print(name + "|");
        for (int k=0; k<values.length; ++k) {
            if (k>0) System.out.print(",");
            System.out.print(values[k]);
        }
        System.out.println();
    }
    static void pair(String name, Hypercomplex value) { show(name, value.re(), value.im()); }
    static void vec(String name, Vector<Double> value) {
        show(name, value.get(0), value.get(1), value.get(2));
    }
    static Vector<Double> v(double a, double b, double c) {
        Vector<Double> result = new Vector<Double>();
        result.add(a); result.add(b); result.add(c); return result;
    }
    public static void main(String[] args) {
        Hypercomplex[] numbers = {new Complex(.4,.2),new Binary(.4,.2),new Dual(.4,.2)};
        String[] names = {"complex", "split", "dual"};
        for (int i=0;i<3;++i) {
            Hypercomplex z=numbers[i]; String n=names[i];
            pair(n+"_square", z.times(z));
            pair(n+"_inverse", z.inverse());
            pair(n+"_exp", z.exp());
            pair(n+"_sin", z.sin());
            pair(n+"_cos", z.cos());
            pair(n+"_log", z.ln());
            vec(n+"_angle_vector", Vectors.vectorFromHypercomplexAngle(z));
        }
        vec("frame_x", Vectors.toNormalAndCompare(v(1,0,0),v(1,2,3),v(2,-1,0)));
        vec("rotation", Vectors.turnedAroundNormal(v(1,2,3),v(0,0,1),.7));
        vec("normal", Vectors.directedConnectingNormal(v(0,0,0),v(1,0,0),v(0,0,2),v(0,1,0)));
        pair("dual_angle", Dual.dualAngle(v(0,0,0),v(1,0,0),v(0,0,2),v(0,1,0)));
        pair("m2r", new M2R(1,2,-3,4).value());
        Joint first=new Joint(); first.setAngle(new Binary(.5,.3)); first.setReal(2);
        Mechanism root=new Mechanism(first);
        Joint second=new Joint(); second.setPos(v(.2,-.1,.3)); second.setAngle(new Dual(.2,.1));
        Mechanism child=new Mechanism(root,second);
        vec("joint_end",root.getAdjustedJoint().getVec());
        vec("child_end",child.getAdjustedJoint().getVec());
        root.getJoint().setAxis(true); root.updateData();
        vec("axis_child_end",child.getAdjustedJoint().getVec());
        pair("guess",new PolynominalGuess(3,2.53,3.04,3.70,4.45,5.31,6.12,6.90).guess());
    }
}
"""

if __name__ == "__main__":
    legacy_probe.main()
