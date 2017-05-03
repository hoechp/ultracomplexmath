package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;

public class VectorTests {

	@Test
	public void testTwoDimensionalVectorFeatures() {
		Complex test1 = new Complex();
		Complex test2 = new Complex();
		double factor = 5;
		Hypercomplex expected = new Complex();
		test1.setCartesian(0, 2);
		test2.setCartesian(-2, -2);
		expected.setCartesian(5, 5);
		test2 = test1.partInDirection(test2).plus(test2).times(factor).mirroredRadialTo(test2);
		Assert.assertEquals(expected, test2);
		Assert.assertTrue(test2.pointsTowards(test2.turnedBy(Math.PI / 2 - Tests.DELTA)));
		Assert.assertTrue(test2.pointsTowards(test2.turnedBy(-Math.PI / 2 + Tests.DELTA)));
		Assert.assertTrue(!test2.pointsTowards(test2.turnedBy(Math.PI / 2 + Tests.DELTA)));
		Assert.assertTrue(!test2.pointsTowards(test2.turnedBy(-Math.PI / 2 - Tests.DELTA)));
	}

	@Test
	public void testDoubleAdditionAndSubstraction() {
		Hypercomplex test1 = new Complex();
		Hypercomplex test2 = new Complex();
		Hypercomplex expected = new Complex();
		// addition
		test1.setCartesian(1, 2);
		test2.setCartesian(3, 4);
		expected.setCartesian(4, 6);
		test2 = test1.plus(test2);
		Assert.assertEquals(expected, test2);
		// addition direct
		test1.setCartesian(1, 2);
		test2.setCartesian(3, 4);
		expected.setCartesian(4, 6);
		test1.add(test2);
		Assert.assertEquals(expected, test1);

		// substraction
		test1.setCartesian(1, 2);
		test2.setCartesian(3, 4);
		expected.setCartesian(-2, -2);
		test2 = test1.minus(test2);
		Assert.assertEquals(expected, test2);
		// substraction direct
		test1.setCartesian(1, 2);
		test2.setCartesian(3, 4);
		expected.setCartesian(-2, -2);
		test1.substract(test2);
		Assert.assertEquals(expected, test1);
	}

	@Test
	public void testDoubleMultiplicationAndDivision() {
		Hypercomplex test = new Complex();
		double factor = 2;
		Hypercomplex expected = new Complex();
		// multiplication
		test.setCartesian(1, 2);
		expected.setCartesian(2, 4);
		test = test.times(factor);
		Assert.assertEquals(expected, test);
		// multiplication direct
		test.setCartesian(1, 2);
		expected.setCartesian(2, 4);
		test.multiply(factor);
		Assert.assertEquals(expected, test);

		double divisor = 2;
		// division
		test.setCartesian(2, 4);
		expected.setCartesian(1, 2);
		test = test.by(divisor);
		Assert.assertEquals(expected, test);
		// division direct
		test.setCartesian(2, 4);
		expected.setCartesian(1, 2);
		test.divide(divisor);
		Assert.assertEquals(expected, test);
	}

}
