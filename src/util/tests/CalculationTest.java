package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Complex;
import util.hypercomplex.calculation.Calculation;
import util.hypercomplex.ultracomplex.Ultra;

public class CalculationTest {

	@Test
	public void testCalculation() {
		Assert.assertTrue(new Calculation("  2  +  2  *  2  ^  2  ").result().equals(new Ultra(10)));
		Assert.assertTrue(new Calculation("0.5").result().equals(new Ultra(0.5)));
		Assert.assertTrue(new Calculation("+0.5").result().equals(new Ultra(0.5)));
		Assert.assertTrue(new Calculation("+ 0.5").result().equals(new Ultra(0.5)));
		Assert.assertTrue(new Calculation("-0.5").result().equals(new Ultra(-0.5)));

		Assert.assertTrue(new Calculation("sqrt(+ 1)").result().equals(new Ultra(1)));
//		Assert.assertTrue(new Calculation("sqrt(- 1)").result().equals(new Ultra(0, 0, 1, 0, 0, 0, 0, 0)));
//		Assert.assertTrue(new Calculation("sqrt(-1)^2").result().equals(new Ultra(-1)));
		// pow((10) * (exp(sqrt(-1))))^(3)
		Assert.assertEquals(
				new Ultra(new Complex(0, Math.PI / 2).exp()),
				Calculation.calculate("exp(" + Math.PI / 2 + "î)")
				);
		Assert.assertTrue(new Calculation("10^(-1)").result().equals(new Ultra(0.1)));
		Assert.assertTrue(new Calculation("10^3").result().equals(new Ultra(1000)));
		Assert.assertTrue(new Calculation("2*3").result().equals(new Ultra(6)));
	}
	
}
