package util.tests;

import java.util.Vector;

import junit.framework.Assert;

import org.junit.Test;

import util.basics.Vectors;
import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.mechanism.Joint;
import util.hypercomplex.mechanism.Mechanism;

public class HypercomplexJointTest {
	
	@Test
	public void testMechanism() {
		double diff = 0.0001;
		Joint j = new Joint();
		Vector<Double> turnNormal = new Vector<Double>();
		for (int i = 0; i < 3; ++i) {
			turnNormal.add((Math.random() * 2 - 1) * 5);
		}
		turnNormal = Vectors.by(turnNormal, Vectors.length(turnNormal));
		double turnAngle = (Math.random() * 2 - 1) * Math.PI;
		j.setNormal(Vectors.turnedAroundNormal(j.getNormal(), turnNormal, turnAngle));
		j.setCompare(Vectors.turnedAroundNormal(j.getCompare(), turnNormal, turnAngle));
		j.setAngle(new Dual(1, 0));
		Mechanism m = new Mechanism(null, j);
		Joint adjust = m.getAdjustedJoint();
		double testValue = Vectors.realAngleAroundNormalWithCompare(adjust.getVec(), j.getNormal(), j.getCompare());
		Assert.assertTrue(Math.abs(1d - testValue) < diff);
		
	}

	@Test
	public void testHypercomplexJoint() {
		double diff = 0.0001;
		// test with default normal and compare vector and default stretch
		Joint hj = new Joint();
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			Hypercomplex angle = null;
			double a = (Math.random() * 2 - 1) * 2 * Math.PI;
			double b = (Math.random() * 2 - 1) * 2 * Math.PI;
			double random = Math.random();
			if (random < 1/3d) {
				angle = new Complex(a, b);
			} else if (random < 2/3d) {
				angle = new Binary(a, b);
			} else {
				angle = new Dual(a, b);
			}
			hj.setAngle(angle);
			Vector<Double> result = hj.getVec();
			//System.out.println(result);
			//System.out.println(Vectors.vectorFromHypercomplexAngle(angle));
			Assert.assertTrue(Vectors.equals(result, Vectors.vectorFromHypercomplexAngle(angle), diff));
		}
	}
	
}
