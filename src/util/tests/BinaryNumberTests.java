package util.tests;


import java.util.ArrayList;

import junit.framework.Assert;


import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Dual;


public class BinaryNumberTests {
	
	@Test
	public void testBinaryRangeFeatures() {
		Binary c1 = new Binary();
		// test if range data is according to definition
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c1 = new Binary("r", Math.random() * 20 - 10, Math.random() * 20 - 10);
			Assert.assertTrue((c1.rangeTo() - c1.rangeFrom()) / 2 - c1.rangeRadius() < 0.000001);
			Assert.assertTrue((c1.rangeTo() + c1.rangeFrom()) / 2 - c1.rangeBase() < 0.000001);
		}
	}

	@Test
	public void testBinaryMultiplicationAndDivision() {
		Binary c1 = new Binary();
		Binary c2 = new Binary();
		// any binary number times another and then divided by it should be the first number again
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c1.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			c2.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Binary compare = c1.times(c2).by(c2);	
			Assert.assertEquals(c1, compare);
		}
	}

	@Test
	public void testBinaryInverse() {
		Binary c = new Binary();
		// any binary number times its binary inverse should be real (img == 0) and should be equaling 1
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Binary test = c.times(c.inverse());
			Binary expected = new Binary(1);	
			Assert.assertEquals(expected, test);
		}
		Binary testB = new Binary();
		testB.set(c);
		testB.setInverse();
		Assert.assertEquals(c.inverse(), testB);
	}
	
	@Test
	public void testPow() {
		Binary base = new Binary();
		Binary exponent = new Binary();
		Binary expected = new Binary();
		Binary result = new Binary();
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
			base.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			exponent.setCartesian(Math.random() * 10 - 5, 0);
			expected = base.pow(exponent.re());
			result = base.pow(exponent);
			if (expected == null) {
				--i;
				continue;
			}
			Assert.assertEquals(expected, result);
		}
		// test real base and complex exponent
		base.setCartesian(2, 0);
		exponent.setCartesian(0, 1);
		result = base.pow(exponent);
		Assert.assertEquals(base.ln().times(exponent).exp(), result);
		
		// hand-calculated z_1 := 3^(2 + i), z_2 := z_1^((2 + i)^(-1)) == 3
		// binary: (2 + i)^(-1) == conjugate(2 + i)/det(2 + i) == 2/3 - i/3
		// had to use conjugate because otherwise it would be illegal
		base.setCartesian(3, 0);
		exponent.setCartesian(2, -1);
		base = base.pow(exponent);
		exponent.set(exponent.inverse());
		expected.setCartesian(3, 0);
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		// random complex cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() + 0.5, (Math.random() - 0.5) * Math.PI);
			do {
				exponent.setPolynominal(Math.random() + 0.5, (Math.random() - 0.5) * Math.PI);
			} while (exponent.im() < 0.1 || exponent.det() == 0);
			result = base.pow(exponent);
			if (result == null) {
				--i;
				continue;
			}
			result = result.pow(exponent.inverse());
			if (result == null || exponent.inverse() == null) {
				--i;
				continue;
			}
			Assert.assertEquals(base, result);
		}
		// random z: z * z == z^2
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 2, 0);
			ArrayList<Double> nullbase = base.diagonalBasis();
			Assert.assertEquals(base.times(base), Binary.fromDiagonalBasis(Math.pow(nullbase.get(0), 2), Math.pow(nullbase.get(1), 2)));
			base.setPolynominal(Math.random() * 2, (Math.random() - 0.5) * Math.PI / 2);
			ArrayList<Double> hyperbolicForm = base.hyperbolicForm();
			Assert.assertEquals(base, Binary.fromHyperbolicForm(hyperbolicForm.get(0), hyperbolicForm.get(1), hyperbolicForm.get(2), hyperbolicForm.get(3)));
			Assert.assertEquals(base.times(base), Binary.fromHyperbolicForm(
					Math.pow(hyperbolicForm.get(0), 2),
					Math.pow(hyperbolicForm.get(1), 2) + Math.pow(hyperbolicForm.get(2), 2),
					2 * hyperbolicForm.get(1) * hyperbolicForm.get(2),
					2 * hyperbolicForm.get(3)
				)); // multiplication like with complex r*e^(phi*i)
			/**
			 * comp: (r_1 * e^(phi_1 * i))^(r_2 * e^(phi_2 * i)) = r_1^r_2 * e^(phi_1 * i * e^(phi_2 * i))
			 * bin: (r_1 * d_1 * e^(phi_1 * i))^(r_2 * d_2 * e^(phi_2 * i)) = r_1^r_2 * d_1^d_2 * e^(phi_1 * E * e^(phi_2 * E))
			 */
			Assert.assertEquals(base, base.exp().ln()); // also ln / exp
			Assert.assertEquals(base.times(base), base.pow(2));
		}
		Assert.assertEquals(new Dual(1), new Dual(1).pow(new Dual(-3)));
		Assert.assertEquals(new Dual(-1), new Dual(-1).pow(new Dual(-3)));
		Assert.assertEquals(new Dual(2, 1).inverse(), new Dual(2, 1).pow(new Dual(-1)));
	}
	
	@Test
	public void testRootsAndPow() {
		Assert.assertEquals(Binary.ONE.times(-1).pow(2), Binary.ONE);
		// take i <= 10 random binary numbers, their n <= 10 n-th roots each
		// and check if those roots^n are the random number again
		Binary c = new Binary();
		for (int i = 0; i < Math.sqrt(Tests.MULTITEST_COUNT); ++i) {
			for (int n = 1; n <= Math.sqrt(Tests.MULTITEST_COUNT); ++n) {
				c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
				ArrayList<? extends Hypercomplex> roots = c.roots(n);
				if (roots != null) {
					for (int k = 0; k < roots.size(); ++k) {
						Hypercomplex fetch = roots.get(k);
						Binary compare = Binary.binary(fetch).pow(n);
						//System.out.println("(" + Binary.binary(fetch) + ")^" + n + " should be " + c);
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
