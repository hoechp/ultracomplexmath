package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;

public class HypercomplexParseTest {

	@Test
	public void testHypercomplexParse() {
		Hypercomplex test = null;
		Hypercomplex ci1 = Complex.ONE.plus(Complex.I).times(-1);
		test = Hypercomplex.parseHypercomplexWeak(ci1.toString());
		Assert.assertEquals(ci1, test);
		Hypercomplex bi1 = Binary.ONE.plus(Binary.I).times(-1);
		test = Hypercomplex.parseHypercomplexWeak(bi1.toString());
		Assert.assertEquals(bi1, test);
		Hypercomplex di1 = Dual.ONE.plus(Dual.I).times(-1);
		test = Hypercomplex.parseHypercomplexWeak(di1.toString());
		Assert.assertEquals(di1, test);
		
		ci1 = Complex.ONE.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(ci1.toString());
		Assert.assertEquals(ci1, test);
		bi1 = Binary.ONE.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(bi1.toString());
		Assert.assertEquals(bi1, test);
		di1 = Dual.ONE.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(di1.toString());
		Assert.assertEquals(di1, test);
		
		ci1 = Complex.I.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(ci1.toString());
		Assert.assertEquals(ci1, test);
		bi1 = Binary.I.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(bi1.toString());
		Assert.assertEquals(bi1, test);
		di1 = Dual.I.times(-1);
		test = Hypercomplex.parseHypercomplexWeak(di1.toString());
		Assert.assertEquals(di1, test);
		
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			double random1 = Math.random() * 1 - 0.5;
			double random2 = Math.random() * 1 - 0.5;
			ci1 = Complex.ONE.times(random1).plus(Complex.I).times(random2);
			test = Hypercomplex.parseHypercomplexWeak(ci1.toString());
			Assert.assertEquals(ci1.toString(), test.toString());
			bi1 = Binary.ONE.times(random1).plus(Binary.I).times(random2);
			test = Hypercomplex.parseHypercomplexWeak(bi1.toString());
			Assert.assertEquals(bi1.toString(), test.toString());
			di1 = Dual.ONE.times(random1).plus(Dual.I).times(random2);
			test = Hypercomplex.parseHypercomplexWeak(di1.toString());
			Assert.assertEquals(di1.toString(), test.toString());
		}
	}
	
}
