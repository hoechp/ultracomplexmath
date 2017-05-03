package util.tests;

import java.util.ArrayList;
import java.util.Vector;

import junit.framework.Assert;


import org.junit.Test;

import util.basics.Vectors;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Dual;

public class DualNumberTests {

	@Test
	public void testDualAngle() {
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			Vector<Double> ts1 = randomVector3D(-2, 2); // adds to all
			Vector<Double> ts2 = randomVector3D(-2, 2); // common normal vector and direct connection
			Vector<Double> ts3 = randomVector3D(-2, 2); // base for first direction vector adding to just ts1
			Vector<Double> ts4 = randomVector3D(-2, 2); // base for second direction vector adding to ts1 and ts2
			Vector<Double> base1 = ts1;
			Vector<Double> base2 = Vectors.plus(ts1, ts2);
			Vector<Double> dir1 = Vectors.cross(ts2, ts3);
			Vector<Double> dir2 = Vectors.cross(ts2, ts4);
			

			base1 = Vectors.plus(base1, Vectors.times(dir1, (Math.random() - 0.5) * 2 * 4));
			base2 = Vectors.plus(base2, Vectors.times(dir2, (Math.random() - 0.5) * 2 * 4));
			
			
			Dual angle = Dual.dualAngle(base1, dir1, base2, dir2);
			// the length of the common connecting normal should be as constructed
			Assert.assertTrue(Math.abs(Vectors.length(ts2) - angle.y()) < 0.00000001);
			// and the angle should be of the same absolute value as the absoluteAngle between dir1 and dir2
			Assert.assertTrue(Math.abs(Vectors.absoluteAngle(dir1, dir2) - Math.abs(angle.x())) < 0.00000001);
			// [testing Vectors.directedConnectingNormal()] the directed connecting normal should be as constructed
			Vector<Double> dcn = Vectors.directedConnectingNormal(base1, dir1, base2, dir2);
			Assert.assertTrue(Vectors.equals(ts2, dcn, 0.00000001));
			// [testing Vectors.closestPoint()] the position where the lines are the closest on line1 should be as constructed
			Assert.assertTrue(Vectors.equals(ts1, Vectors.closestPoint(base1, dir1, base2, dir2), 0.00000001));
			// [testing Vectors.normalize()] the normalization shouldn't change the dual angle
			Vectors.normalize(base1, dir1, base2, dir2);
			Dual angle2 = Dual.dualAngle(base1, dir1, base2, dir2);
			Assert.assertEquals(angle, angle2);
			// [testing Dual.trancend()] (both normalized) line1-data transcended by the dual angle should be line2-data
			Dual.transcend(base1, dir1, dcn, angle);
			Assert.assertTrue(Vectors.equals(base1, base2, 0.00000001));
			Assert.assertTrue(Vectors.equals(dir1, dir2, 0.00000001));
		}
	}
	
	private static Vector<Double> randomVector3D(double from, double to) {
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < 3; ++i) {
			result.add(from + Math.random() * (to - from));
		}
		return result;
	}
	
	@Test
	public void testDualSphereProjection() {
		Dual d = new Dual();
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			d.setPolynominal(Math.random() * 10, Math.random() * 2 * Math.PI);
			// any 2-dim. dual number projected to the 3-dim. sphere should have the 3-dim. length of 1
			Assert.assertTrue(
						Math.abs(
							-1d
							+d.unitSpherePosition().get(0)*d.unitSpherePosition().get(0)
							+d.unitSpherePosition().get(1)*d.unitSpherePosition().get(1)
							+d.unitSpherePosition().get(2)*d.unitSpherePosition().get(2)
						) < 0.000001
					);
			// any dual number projected to the sphere and back should be the same dual number again
			Assert.assertEquals(d, Dual.fromUnitSpherePosition(d.unitSpherePosition()));
		}
	}

	@Test
	public void testDualMultiplicationAndDivision() {
		Dual d1 = new Dual();
		Dual d2 = new Dual();
		// any dual number times another and then divided by it should be the first number again
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			d1.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			d2.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Dual compare = d1.times(d2).by(d2);	
			Assert.assertEquals(d1, compare);
		}
	}

	@Test
	public void testDualInverse() {
		Dual c = new Dual();
		// any dual number times its dual inverse should be real (img == 0) and should be equaling 1
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Dual test = c.times(c.inverse());
			Dual expected = new Dual(1);	
			Assert.assertEquals(expected, test);
		}
	}
	
	@Test
	public void testPow() {
		Dual base = new Dual();
		Dual exponent = new Dual();
		Dual expected = new Dual();
		Dual result = new Dual();
		 // test real bases and real exponents (like Math.pow)
		base.setCartesian(2, 0);
		for (double i = -Tests.MULTITEST_COUNT / 4; i <= Tests.MULTITEST_COUNT / 4; i += 0.5) {
			exponent.setCartesian(i, 0);
			expected.setCartesian(Math.pow(2, i), 0);
			result = base.pow(exponent);
			Assert.assertEquals(expected, result);
		}
		// test complex bases and real exponents
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 100, (Math.random() - 0.5) * Math.PI);
			exponent.setCartesian(Math.random() * 10 - 5, 0);
			expected = base.pow(exponent.re());
			result = base.pow(exponent);
			Assert.assertEquals(expected, result);
		}
		// test complex base and complex exponent
		base.setCartesian(2, 2);
		exponent.setCartesian(0, 1);
		expected.setCartesian(1, Math.log(2));
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		// test real base and complex exponent
		base.setCartesian(2, 0);
		exponent.setCartesian(0, 1);
		expected.setCartesian(1, Math.log(2)); // with complex the result would be the same but these would be polynominal ordinates
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		
		// hand-calculated z_1 := 3^(2 + i), z_2 := z_1^((2 + i)^(-1)) == 3
		// dual: (2 + i)^(-1) == conjugate(2 + i)/det(2 + i) == 1/2 - i/4
		base.setCartesian(3, 0);
		exponent.setCartesian(2, 1);
		base = base.pow(exponent);
		exponent.setCartesian(1d/2, -1d/4);
		expected.setCartesian(3, 0);
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		// random complex cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() + 0.5, (Math.random() - 0.5) * Math.PI);
			do {
				exponent.setPolynominal(Math.random() + 0.5, (Math.random() - 0.5) * Math.PI);
			} while (exponent.im() < 0.1 || exponent.det() == 0);
			result.set(base.pow(exponent).pow(exponent.inverse()));
			Assert.assertEquals(base.toString(), result.toString());
		}
		// random z: z * z == z^2
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setCartesian(Math.random() * 4 + 1, Math.random() * 4 - 2);
			Assert.assertEquals(base.times(base), base.pow(2));
			base.setPolynominal(Math.random() * 4, (Math.random() - 0.5) * Math.PI);
			Assert.assertEquals(base, base.ln().exp()); // also ln / exp
			Assert.assertEquals(Dual.E.pow(base), base.exp()); // also ln / exp
		}
		Assert.assertEquals(new Dual(1), new Dual(1).pow(new Dual(-3)));
		Assert.assertEquals(new Dual(-1), new Dual(-1).pow(new Dual(-3)));
		Assert.assertEquals(new Dual(2, 1).inverse(), new Dual(2, 1).pow(new Dual(-1)));
	}
	
	@Test
	public void testRootsAndPow() {
		// take i <= 10 random dual numbers, their n <= 10 n-th roots each
		// and check if those roots^n are the random number again
		Dual c = new Dual();
		for (int i = 0; i < Math.sqrt(Tests.MULTITEST_COUNT); ++i) {
			for (int n = 1; n <= Math.sqrt(Tests.MULTITEST_COUNT); ++n) {
				c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
				ArrayList<? extends Hypercomplex> roots = c.roots(n);
				if (roots != null) {
					for (int k = 0; k < roots.size(); ++k) {
						Hypercomplex fetch = roots.get(k);
						Dual compare = Dual.dual(fetch).pow(n);
						//System.out.println("(" + Dual.dual(fetch) + ")^" + n + " should be " + c);
						Assert.assertEquals(c, compare);
					}
				} else {
					--n;
					continue;
				}
			}
		}
	}
	
}
