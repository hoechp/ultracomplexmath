package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Dual;

public class TestHypercomplexTrigonometrics {
	
	@Test
	public void testNonHyperbolicHypercomplexTrigonometrics() {

		// test non-hyperbolic trigonometric functions and inverses for complex numbers in both directions
		Hypercomplex c = new Complex(0.5, 0.25);
		Assert.assertEquals(c, c.sin().asin());
		Assert.assertEquals(c, c.asin().sin());
		Assert.assertEquals(c, c.cos().acos());
		Assert.assertEquals(c, c.acos().cos());
		Assert.assertEquals(c, c.tan().atan());
		Assert.assertEquals(c, c.atan().tan());
		Assert.assertEquals(c, c.cot().acot());
		Assert.assertEquals(c, c.acot().cot());
		Assert.assertEquals(c, c.sec().asec());
		Assert.assertEquals(c, c.asec().sec());
		Assert.assertEquals(c, c.csc().acsc());
		Assert.assertEquals(c, c.acsc().csc());
		/*
		System.out.println(c + " == " + c.sin().asin());
		System.out.println(c + " == " + c.asin().sin());
		System.out.println(c + " == " + c.cos().acos());
		System.out.println(c + " == " + c.acos().cos());
		System.out.println(c + " == " + c.tan().atan());
		System.out.println(c + " == " + c.atan().tan());
		System.out.println(c + " == " + c.cot().acot());
		System.out.println(c + " == " + c.acot().cot());
		System.out.println(c + " == " + c.sec().asec());
		System.out.println(c + " == " + c.asec().sec());
		System.out.println(c + " == " + c.csc().acsc());
		System.out.println(c + " == " + c.acsc().csc());
		*/

		// test non-hyperbolic trigonometric functions and inverses for dual numbers in both directions
		Dual d = new Dual(0.5, 0.25);
		Dual d2 = new Dual(1.5, 0.25);
		Assert.assertEquals(d, d.sin().asin());
		Assert.assertEquals(d, d.asin().sin());
		Assert.assertEquals(d, d.cos().acos());
		Assert.assertEquals(d, d.acos().cos());
		Assert.assertEquals(d, d.tan().atan());
		Assert.assertEquals(d, d.atan().tan());
		Assert.assertEquals(d, d.cot().acot());
		Assert.assertEquals(d, d.acot().cot());
		Assert.assertEquals(d, d.sec().asec());
		Assert.assertEquals(d2, d2.asec().sec());
		Assert.assertEquals(d, d.csc().acsc());
		Assert.assertEquals(d2, d2.acsc().csc());
		/*
		System.out.println(d + " == " + d.sin().asin());
		System.out.println(d + " == " + d.asin().sin());
		System.out.println(d + " == " + d.cos().acos());
		System.out.println(d + " == " + d.acos().cos());
		System.out.println(d + " == " + d.tan().atan());
		System.out.println(d + " == " + d.atan().tan());
		System.out.println(d + " == " + d.cot().acot());
		System.out.println(d + " == " + d.acot().cot());
		System.out.println(d + " == " + d.sec().asec());
		System.out.println(d2 + " == " + d2.asec().sec());
		System.out.println(d + " == " + d.csc().acsc());
		System.out.println(d2 + " == " + d2.acsc().csc());
		*/
		
		// test non-hyperbolic trigonometric functions and inverses for binary numbers in both directions
		Binary b = new Binary(0.5, 0.25);
		Binary b2 = new Binary(1.5, 0.25);
		Assert.assertEquals(b, b.sin().asin());
		Assert.assertEquals(b, b.asin().sin());
		Assert.assertEquals(b, b.cos().acos());
		Assert.assertEquals(b, b.acos().cos());
		Assert.assertEquals(b, b.tan().atan());
		Assert.assertEquals(b, b.atan().tan());
		Assert.assertEquals(b, b.cot().acot());
		Assert.assertEquals(b, b.acot().cot());
		Assert.assertEquals(b, b.sec().asec());
		Assert.assertEquals(b2, b2.asec().sec());
		Assert.assertEquals(b, b.csc().acsc());
		Assert.assertEquals(b2, b2.acsc().csc());
		/*
		System.out.println(b + " == " + b.sin().asin());
		System.out.println(b + " == " + b.asin().sin());
		System.out.println(b + " == " + b.cos().acos());
		System.out.println(b + " == " + b.acos().cos());
		System.out.println(b + " == " + b.tan().atan());
		System.out.println(b + " == " + b.atan().tan());
		System.out.println(b + " == " + b.cot().acot());
		System.out.println(b + " == " + b.acot().cot());
		System.out.println(b + " == " + b.sec().asec());
		System.out.println(b2 + " == " + b2.asec().sec());
		System.out.println(b + " == " + b.csc().acsc());
		System.out.println(b2 + " == " + b2.acsc().csc());
		*/

		// make sure all non-hyperbolic trigonometric functions are different for each algebra
		Assert.assertFalse(Complex.complex(d.sin()).equals(c.sin()));
		Assert.assertFalse(Complex.complex(b.sin()).equals(c.sin()));
		Assert.assertFalse(Dual.dual(b.sin()).equals(d.sin()));
		Assert.assertFalse(Complex.complex(d.asin()).equals(c.asin()));
		Assert.assertFalse(Complex.complex(b.asin()).equals(c.asin()));
		Assert.assertFalse(Dual.dual(b.asin()).equals(d.asin()));
		Assert.assertFalse(Complex.complex(d.cos()).equals(c.cos()));
		Assert.assertFalse(Complex.complex(b.cos()).equals(c.cos()));
		Assert.assertFalse(Dual.dual(b.cos()).equals(d.cos()));
		Assert.assertFalse(Complex.complex(d.acos()).equals(c.acos()));
		Assert.assertFalse(Complex.complex(b.acos()).equals(c.acos()));
		Assert.assertFalse(Dual.dual(b.acos()).equals(d.acos()));
		Assert.assertFalse(Complex.complex(d.tan()).equals(c.tan()));
		Assert.assertFalse(Complex.complex(b.tan()).equals(c.tan()));
		Assert.assertFalse(Dual.dual(b.tan()).equals(d.tan()));
		Assert.assertFalse(Complex.complex(d.atan()).equals(c.atan()));
		Assert.assertFalse(Complex.complex(b.atan()).equals(c.atan()));
		Assert.assertFalse(Dual.dual(b.atan()).equals(d.atan()));
		Assert.assertFalse(Complex.complex(d.cot()).equals(c.cot()));
		Assert.assertFalse(Complex.complex(b.cot()).equals(c.cot()));
		Assert.assertFalse(Dual.dual(b.cot()).equals(d.cot()));
		Assert.assertFalse(Complex.complex(d.acot()).equals(c.acot()));
		Assert.assertFalse(Complex.complex(b.acot()).equals(c.acot()));
		Assert.assertFalse(Dual.dual(b.acot()).equals(d.acot()));
		Assert.assertFalse(Complex.complex(d.sec()).equals(c.sec()));
		Assert.assertFalse(Complex.complex(b.sec()).equals(c.sec()));
		Assert.assertFalse(Dual.dual(b.sec()).equals(d.sec()));
		Assert.assertFalse(Complex.complex(d.asec()).equals(c.asec()));
		Assert.assertFalse(Complex.complex(b.asec()).equals(c.asec()));
		Assert.assertFalse(Dual.dual(b.asec()).equals(d.asec()));
		Assert.assertFalse(Complex.complex(d.csc()).equals(c.csc()));
		Assert.assertFalse(Complex.complex(b.csc()).equals(c.csc()));
		Assert.assertFalse(Dual.dual(b.csc()).equals(d.csc()));
		Assert.assertFalse(Complex.complex(d.acsc()).equals(c.acsc()));
		Assert.assertFalse(Complex.complex(b.acsc()).equals(c.acsc()));
		Assert.assertFalse(Dual.dual(b.acsc()).equals(d.acsc()));
		
	}
	
	@Test
	public void testHyperbolicHypercomplexTrigonometrics() {

		// test hyperbolic trigonometric functions and inverses for complex numbers in both directions
		Hypercomplex c = new Complex(0.5, 0.25);
		Hypercomplex c2 = new Complex(1.5, 0.25);
		Assert.assertEquals(c, c.sinh().asinh());
		Assert.assertEquals(c, c.asinh().sinh());
		Assert.assertEquals(c, c.cosh().acosh());
		Assert.assertEquals(c, c.acosh().cosh());
		Assert.assertEquals(c, c.tanh().atanh());
		Assert.assertEquals(c, c.atanh().tanh());
		Assert.assertEquals(c, c.coth().acoth());
		Assert.assertEquals(c2, c2.acoth().coth());
		Assert.assertEquals(c, c.sech().asech());
		Assert.assertEquals(c, c.asech().sech());
		Assert.assertEquals(c, c.csch().acsch());
		Assert.assertEquals(c, c.acsch().csch());
		/*
		System.out.println(c + " == " + c.sinh().asinh());
		System.out.println(c + " == " + c.asinh().sinh());
		System.out.println(c + " == " + c.cosh().acosh());
		System.out.println(c + " == " + c.acosh().cosh());
		System.out.println(c + " == " + c.tanh().atanh());
		System.out.println(c + " == " + c.atanh().tanh());
		System.out.println(c + " == " + c.coth().acoth());
		System.out.println(c2 + " == " + c2.acoth().coth());
		System.out.println(c + " == " + c.sech().asech());
		System.out.println(c + " == " + c.asech().sech());
		System.out.println(c + " == " + c.csch().acsch());
		System.out.println(c + " == " + c.acsch().csch());
		*/

		// test hyperbolic trigonometric functions and inverses for dual numbers in both directions
		Dual d = new Dual(0.5, 0.25);
		Dual d2 = new Dual(1.5, 0.25);
		Assert.assertEquals(d, d.sinh().asinh());
		Assert.assertEquals(d, d.asinh().sinh());
		Assert.assertEquals(d, d.cosh().acosh());
		Assert.assertEquals(d2, d2.acosh().cosh());
		Assert.assertEquals(d, d.tanh().atanh());
		Assert.assertEquals(d, d.atanh().tanh());
		Assert.assertEquals(d, d.coth().acoth());
		Assert.assertEquals(d2, d2.acoth().coth());
		Assert.assertEquals(d, d.sech().asech());
		Assert.assertEquals(d, d.asech().sech());
		Assert.assertEquals(d, d.csch().acsch());
		Assert.assertEquals(d, d.acsch().csch());
		/*
		System.out.println(d + " == " + d.sinh().asinh());
		System.out.println(d + " == " + d.asinh().sinh());
		System.out.println(d + " == " + d.cosh().acosh());
		System.out.println(d2 + " == " + d2.acosh().cosh());
		System.out.println(d + " == " + d.tanh().atanh());
		System.out.println(d + " == " + d.atanh().tanh());
		System.out.println(d + " == " + d.coth().acoth());
		System.out.println(d2 + " == " + d2.acoth().coth());
		System.out.println(d + " == " + d.sech().asech());
		System.out.println(d + " == " + d.asech().sech());
		System.out.println(d + " == " + d.csch().acsch());
		System.out.println(d + " == " + d.acsch().csch());
		*/

		// test hyperbolic trigonometric functions and inverses for binary numbers in both directions
		Binary b = new Binary(0.5, 0.25);
		Binary b2 = new Binary(1.5, 0.25);
		Assert.assertEquals(b, b.sinh().asinh());
		Assert.assertEquals(b, b.asinh().sinh());
		Assert.assertEquals(b, b.cosh().acosh());
		Assert.assertEquals(b2, b2.acosh().cosh());
		Assert.assertEquals(b, b.tanh().atanh());
		Assert.assertEquals(b, b.atanh().tanh());
		Assert.assertEquals(b, b.coth().acoth());
		Assert.assertEquals(b2, b2.acoth().coth());
		Assert.assertEquals(b, b.sech().asech());
		Assert.assertEquals(b, b.asech().sech());
		Assert.assertEquals(b, b.csch().acsch());
		Assert.assertEquals(b, b.acsch().csch());
		/*
		System.out.println(b + " == " + b.sinh().asinh());
		System.out.println(b + " == " + b.asinh().sinh());
		System.out.println(b + " == " + b.cosh().acosh());
		System.out.println(b2 + " == " + b2.acosh().cosh());
		System.out.println(b + " == " + b.tanh().atanh());
		System.out.println(b + " == " + b.atanh().tanh());
		System.out.println(b + " == " + b.coth().acoth());
		System.out.println(b2 + " == " + b2.acoth().coth());
		System.out.println(b + " == " + b.sech().asech());
		System.out.println(b + " == " + b.asech().sech());
		System.out.println(b + " == " + b.csch().acsch());
		System.out.println(b + " == " + b.acsch().csch());
		*/

		// make sure all hyperbolic trigonometric functions are different for each algebra
		Assert.assertFalse(Complex.complex(d.sinh()).equals(c.sinh()));
		Assert.assertFalse(Complex.complex(b.sinh()).equals(c.sinh()));
		Assert.assertFalse(Dual.dual(b.sinh()).equals(d.sinh()));
		Assert.assertFalse(Complex.complex(d.asinh()).equals(c.asinh()));
		Assert.assertFalse(Complex.complex(b.asinh()).equals(c.asinh()));
		Assert.assertFalse(Dual.dual(b.asinh()).equals(d.asinh()));
		Assert.assertFalse(Complex.complex(d.cosh()).equals(c.cosh()));
		Assert.assertFalse(Complex.complex(b.cosh()).equals(c.cosh()));
		Assert.assertFalse(Dual.dual(b.cosh()).equals(d.cosh()));
		Assert.assertFalse(Complex.complex(d.acosh()).equals(c.acosh()));
		Assert.assertFalse(Complex.complex(b2.acosh()).equals(c2.acosh()));
		Assert.assertFalse(Dual.dual(b2.acosh()).equals(d2.acosh()));
		Assert.assertFalse(Complex.complex(d.tanh()).equals(c.tanh()));
		Assert.assertFalse(Complex.complex(b.tanh()).equals(c.tanh()));
		Assert.assertFalse(Dual.dual(b.tanh()).equals(d.tanh()));
		Assert.assertFalse(Complex.complex(d.atanh()).equals(c.atanh()));
		Assert.assertFalse(Complex.complex(b.atanh()).equals(c.atanh()));
		Assert.assertFalse(Dual.dual(b.atanh()).equals(d.atanh()));
		Assert.assertFalse(Complex.complex(d.coth()).equals(c.coth()));
		Assert.assertFalse(Complex.complex(b.coth()).equals(c.coth()));
		Assert.assertFalse(Dual.dual(b.coth()).equals(d.coth()));
		Assert.assertFalse(Complex.complex(d.acoth()).equals(c.acoth()));
		Assert.assertFalse(Complex.complex(b2.acoth()).equals(c2.acoth()));
		Assert.assertFalse(Dual.dual(b2.acoth()).equals(d2.acoth()));
		Assert.assertFalse(Complex.complex(d.sech()).equals(c.sech()));
		Assert.assertFalse(Complex.complex(b.sech()).equals(c.sech()));
		Assert.assertFalse(Dual.dual(b.sech()).equals(d.sech()));
		Assert.assertFalse(Complex.complex(d.asech()).equals(c.asech()));
		Assert.assertFalse(Complex.complex(b.asech()).equals(c.asech()));
		Assert.assertFalse(Dual.dual(b.asech()).equals(d.asech()));
		Assert.assertFalse(Complex.complex(d.csch()).equals(c.csch()));
		Assert.assertFalse(Complex.complex(b.csch()).equals(c.csch()));
		Assert.assertFalse(Dual.dual(b.csch()).equals(d.csch()));
		Assert.assertFalse(Complex.complex(d.acsch()).equals(c.acsch()));
		Assert.assertFalse(Complex.complex(b.acsch()).equals(c.acsch()));
		Assert.assertFalse(Dual.dual(b.acsch()).equals(d.acsch()));
		
	}

}
