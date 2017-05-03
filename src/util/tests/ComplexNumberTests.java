package util.tests;


import java.util.ArrayList;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;

public class ComplexNumberTests {
	
	@Test
	public void testEquals() {
		Hypercomplex a = new Complex();
		Hypercomplex b = new Complex();
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			a.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			b = a.clone();
			Assert.assertTrue(a.equals(b));
			Assert.assertFalse(a.times(1.01).equals(b));
		}
	}
	
	@Test
	public void testHashCode() {
		Hypercomplex a = new Complex();
		Hypercomplex b = new Complex();
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			a.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			b = a.clone();
			Assert.assertTrue(a.hashCode() == b.hashCode());
		}
	}

	@Test
	public void testComplexMultiplicationAndDivision() {
		Hypercomplex c1 = new Complex();
		Hypercomplex c2 = new Complex();
		// any complex number times another and then divided by it should be the first number again
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c1.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			c2.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Hypercomplex compare = c1.times(c2).by(c2);	
			Assert.assertEquals(c1, compare);
		}
	}

	@Test
	public void testComplexConjugateAndInverse() {
		Hypercomplex c = new Complex();
		// any complex number times its complex conjugate should be real (img == 0)
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			c.multiply(c.conjugate());
			Assert.assertEquals(0, c.im(), Tests.DELTA);
		}
		// any complex number times its complex inverse should be real (img == 0) and should be equaling 1
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
			Hypercomplex test = c.times(c.inverse());
			Hypercomplex expected = new Complex(1);	
			Assert.assertEquals(expected, test);
		}
	}
	
	@Test
	public void testRootsAndPow() {
		// test complex pq-formula with x^2 - 1 = 0
		// x^2 - 1 = 0
		// => x1/2 = -p/2 +- ((p/2)^2 - q)
		// => p = 0
		// q = 1,
		// x1/2 = +-sqrt(1)
		// x1/2 = +-1
		Hypercomplex q = new Complex(1);
		Hypercomplex expectedX1 = new Complex(1);
		Hypercomplex expectedX2 = new Complex(-1);
		Hypercomplex x1 = q.roots(2).get(0);
		Hypercomplex x2 = q.roots(2).get(1);
		Assert.assertEquals(expectedX1, x1);
		Assert.assertEquals(expectedX2, x2);
		// take i <= 10 random complex numbers, their n <= 10 n-th roots each
		// and check if those roots^n are the random number again
		Hypercomplex c = new Complex();
		for (int i = 0; i < Math.sqrt(Tests.MULTITEST_COUNT); ++i) {
			for (int n = 1; n <= Math.sqrt(Tests.MULTITEST_COUNT); ++n) {
				c.setPolynominal(Math.random() * 100, Math.random() * 2 * Math.PI);
				c.setPolynominal(1, 0);
				
				ArrayList<? extends Hypercomplex> roots = c.roots(n);
				for (int k = 0; k < n; ++k) {
					Hypercomplex compare = roots.get(k).pow(n);
					Assert.assertEquals(c, compare);
				}
			}
		}
	}
	
	@Test
	public void testLog() {
		// complex case # 1
		Hypercomplex base = new Complex();
		base.setCartesian(2, 2);
		Hypercomplex result = base.ln();
		Hypercomplex expected = new Complex();
		expected.setCartesian(3 * Math.log(2) / 2, Math.PI / 4);
		Assert.assertEquals(expected, result);
		// complex case #2
		base.setCartesian(-1, 1);
		result = base.ln();
		expected.setCartesian(Math.log(2) / 2, 3 * Math.PI / 4);
		Assert.assertEquals(expected, result);
		// real case
		base.setCartesian(2, 0);
		result = base.ln(); // has to be the normal ln(2)
		expected.setCartesian(Math.log(2), 0);
		Assert.assertEquals(expected, result);
		// negative real case
		base.setCartesian(-2, 0);
		result = base.ln();
		expected.setCartesian(Math.log(2), Math.PI);
		Assert.assertEquals(expected, result);
		// random complex cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 100000, Math.random() * 2 * Math.PI);
			result = Complex.exp(base.ln());
			Assert.assertEquals(base, result);
		}
	}
	
	@Test
	public void testIsLog() {
		Hypercomplex base = new Complex();
		Hypercomplex result = new Complex();
		Hypercomplex additive = new Complex(0, 2 * Math.PI);
		// super EVIL constructed random complex test cases
		for (int i = 0; i < Tests.MULTITEST_COUNT / 10; ++i) {
			base.setPolynominal(Math.random() * 10, Math.random() * 2 * Math.PI);
			result = base.ln();
			for (int j = -5; j < 5; ++j) {
				Assert.assertTrue(additive.times(j).plus(result).isLn(base));
				Assert.assertFalse(additive.times(j + 0.001).plus(result).isLn(base));
			}
		}
	}
	
	@Test
	public void testPow() {
		Hypercomplex base = new Complex();
		Hypercomplex exponent = new Complex();
		Hypercomplex expected = new Complex();
		Hypercomplex result = new Complex();
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
			Assert.assertEquals(expected, result);
		}
		// test complex base and complex exponent
		base.setCartesian(0, 1);
		exponent.setCartesian(0, 1);
		expected.setCartesian(Math.exp(-Math.PI / 2), 0);
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		// test real base and complex exponent
		base.setCartesian(2, 0);
		exponent.setCartesian(0, 1);
		expected.setPolynominal(1, Math.log(2));
		result = base.pow(exponent);
		Assert.assertEquals(expected, result);
		
		// hand-calculated z_1 := 3^(2 + i), z_2 := z_1^((2 + i)^(-1)) == 3
		// dual: (2 + i)^(-1) == conjugate(2 + i)/det(2 + i) == 2/5 - i/5
		base.setCartesian(3, 0);
		exponent.setCartesian(2, 1);
		base = base.pow(exponent);
		exponent.setCartesian(2d/5, -1d/5);
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
			Assert.assertEquals(base, result);
		}
		// random z: z * z == z^2
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 2, Math.random() * 2 * Math.PI);
			Assert.assertEquals(base.times(base), base.pow(2));
			Assert.assertEquals(base.toString(), base.exp().ln().toString()); // also ln / exp
		}
		
		// select random complex cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			// (when writing z^w:) log(z) * w << 1 && IM(log(z) * w) >> 0 => z^w^(w.inverse()) != z (different principal value)
			// also when phi_1 and phi_2 are both nearly at -PI or both nearly at PI it usually changes the principal value
			base.setPolynominal(Math.random() * Math.sqrt(Math.PI) + Math.E, Math.random() * 0.5 * Math.PI);
			exponent.setPolynominal(Math.random() + 1, Math.random() * 0.5 * Math.PI);
			result = base.pow(exponent.inverse()).pow(exponent);
			Assert.assertEquals(base, result);
		}
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			// (when writing z^w:) RE(log(z) * w) << 1 && IM(log(z) * w) >> 0 => z^w^(w.inverse()) != z (different principal value)
			base.setPolynominal(Math.random() * 10 + 1, Math.random() * 0.5 * Math.PI);
			exponent.setPolynominal(Math.random() * 10 + 1, Math.random() * 0.5 * Math.PI);
			result = base.pow(exponent.times(-1)).inverse();
			Assert.assertEquals(base.pow(exponent), result);
		}
		// EVIL select random complex cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 10 + 1, Math.random() * 0.5 * Math.PI);
			exponent.setPolynominal(Math.random() * 100, Math.random() * 0.5 * Math.PI);
			result = base.pow(exponent);
			Assert.assertTrue(result.isPow(base, exponent));
		}
	}
	
	@Test
	public void testIsPow() {
		Hypercomplex base = new Complex();
		Hypercomplex exponent = new Complex();
		Hypercomplex result = new Complex();
		Hypercomplex factor = new Complex();
		// super EVIL constructed random complex test cases
		for (int i = 0; i < 5; ++i) {
			base.setPolynominal(Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent.setPolynominal(Math.random() * 2, Math.random() * Math.PI - Math.PI / 2);
			result = base.pow(exponent);
			for (int j = -Tests.MULTITEST_COUNT / 10; j < Tests.MULTITEST_COUNT / 10; ++j) {
				factor = Complex.exp(Complex.I.times(2 * Math.PI * j).times(exponent));
				Assert.assertTrue(result.times(factor).isPow(base, exponent));
			}
		}
		// EVIL constructed random complex (and complete) test cases
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base.setPolynominal(Math.random() * 10 + 1, Math.random() * 2 * Math.PI);
			int rootCount = (int)(2 + Math.random() * 9);
			ArrayList<? extends Hypercomplex> results = base.roots(rootCount);
			for (int j = 0; j < rootCount; ++j) { // check if the roots are all base.pow(1/rootCount)
				Assert.assertTrue(results.get(j).isPow(base, new Complex(1d / rootCount)));
			}
		}
		// EVIL constructed complex extra test cases
		base = Complex.ONE;
		exponent.setCartesian(Math.sqrt(2), 0);
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) { // 1^sqrt(2) ~= unit circle
			result = new Complex("p", 1, Math.random() * 2 * Math.PI);
			Assert.assertTrue(result.isPow(base, exponent));
		}
	}
	
	@Test
	public void testIsNotPow() {
		/*
		 * since there are errors in double value:
		 *   a complex number to the power of a real number as base means:
		 *     when you check if a number is a solution to that,
		 *     it's always the case that all solutions with
		 *     the same length appear to be valid.
		 *     (when generally (if exponent is rational) there are
		 *     only a finite number of solutions) 
		 * so because of that you cannot test against that.
		 * 
		 * TEST IF (RADIAL) GAPS BETWEEN DOTS COULD BE DETECTED <- 0*re + im
		 * [MAYBE ALSO PERPENDICULAR GAPS WHEN EXPONENT HAS IMAGINARY PART] <- re + im
		 * OR COULD EVEN THE GAPS BETWEEN THE SOLUTIONS OF REAL EXPONENTS BE DETECTED WITH THE USED METHOD??
		 * definition of GAP:
		 *   gap between SOLUTIONS (no offset to the line between actual solutions)
		 */
		Hypercomplex base;
		Hypercomplex exponent;
		Hypercomplex toTest;
		// SINGLE POINT (any change)
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = Complex.ZERO;
			Hypercomplex littleAdd = new Complex("p", Math.random() + 0.01, Math.random() * 2 * Math.PI);
			toTest = base.pow(exponent);
			Assert.assertTrue(toTest.isPow(base, exponent));
			toTest.add(littleAdd);
			Assert.assertFalse(toTest.isPow(base, exponent));
		}
		// LINE-TYPE (rotational change)
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(0, Math.random() * 10 + 0.01);
			toTest = base.pow(exponent);
			Assert.assertTrue(toTest.isPow(base, exponent));
			toTest.turn(0.01);
			Assert.assertFalse(toTest.isPow(base, exponent));
		}
		// CIRCULAR-TYPE (distance change)
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(Math.random() * 2 + 0.01, 0);
			toTest = base.pow(exponent);
			double littleAddFactor = (toTest.r() + 0.01) / toTest.r();
			Assert.assertTrue(toTest.isPow(base, exponent));
			toTest.multiply(littleAddFactor);
			Assert.assertFalse(toTest.isPow(base, exponent));
		}
		// SPIRAL-TYPE (rotational change)
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(Math.random() * 10 + 0.01, Math.random() * 10 + 0.01);
			toTest = base.pow(exponent);
			Assert.assertTrue(toTest.isPow(base, exponent));
			toTest.turn(0.01);
			Assert.assertFalse(toTest.isPow(base, exponent));
			toTest.turn(-0.02);
			Assert.assertFalse(toTest.isPow(base, exponent));
		}
		// SPIRAL-TYPE (distance change)
		boolean multiTest = false; // because full rotations can be made occasionally its still a solution
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(Math.random() * 10 + 0.01, Math.random() * 10 + 0.01);
			toTest = base.pow(exponent);
			double littleAddFactor = (toTest.r() + 0.01) / toTest.r();
			toTest.multiply(littleAddFactor);
			if (!multiTest && !toTest.isPow(base, exponent)) {
				multiTest = true;
			}
		}
		Assert.assertTrue(multiTest);
		// VOID BETWEEN LINE-TYPE SOLUTIONS (distance change)
		multiTest = false; // if some gaps are found it would be plenty validation
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(0, Math.random() * 10 + 0.01);
			toTest = base.pow(exponent);
			double littleAddFactor = (toTest.r() + 0.01) / toTest.r();
			toTest.multiply(littleAddFactor);
			if (!multiTest && !toTest.isPow(base, exponent)) {
				multiTest = true;
			}
		}
		Assert.assertTrue(multiTest);
		// VOID BETWEEN SPIRAL-TYPE SOLUTIONS (spiral change)
		multiTest = false; // if some gaps are found it would be plenty validation
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			base = new Complex("p", Math.random() * 10 + 0.01, Math.random() * 2 * Math.PI);
			exponent = new Complex(Math.random() * 10 + 0.01, Math.random() * 10 + 0.01);
			toTest = base.pow(exponent);
			double j = (int)(Math.random() * 10 - 5) + 0.5;
			Hypercomplex factor = Complex.exp(Complex.I.times(2 * Math.PI * j).times(exponent));
			toTest.multiply(factor);
			if (!multiTest && !toTest.isPow(base, exponent)) {
				multiTest = true;
			}
		}
		Assert.assertTrue(multiTest);
		
		// NOW THE FINAL SOLUTION TO THE C^R-PROBLEM: -> MAKE IT C^Q:
		Assert.assertTrue(Complex.ONE.isPow(Complex.ONE, 1, 4));
		// now a hundred million-st part of a degree offset at the distance of one is enough to see its no solution
		Assert.assertFalse(new Complex("p", 1, Math.toRadians(1e-8)).isPow(Complex.ONE, 1, 4));
		Assert.assertFalse(new Complex("p", 1, Math.PI / 4).isPow(Complex.ONE, 1, 4));
		Assert.assertTrue(new Complex("p", 1, Math.PI / 2).isPow(Complex.ONE, 1, 4));
	}

}