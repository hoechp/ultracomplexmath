package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.ultracomplex.Ultra;

public class UltraTest {

	@Test
	public void testUltra() {
		
		/**
		 * here basic addition and multiplication is tested.
		 * along with building a conjugate, determinant and, with that, the inverse.
		 * (inverse() == conjugate() / det())
		 */
		Ultra a = new Ultra(2, 3, 5, 0, 0, 0, 0, 0);
		Ultra b = new Ultra(2, 0, 0, 0, 0, 0, 0, 0);
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());
		
		a = new Ultra(0, 2, 3, 0, 5, 0, 0, 0);
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());
		
		/**
		 * in the following example, the inverse contains all 8 dimensions and its inverse,
		 * like expected, is the original (4-dimensional) number again.
		 * 
		 * usually though, if all 8 dimensions are used, especially with big (or small) numbers,
		 * the conjugate is such a huge (or tiny) number (containing 127 factors of the size of the original number),
		 * that the inverse of the inverse only wildly matches the original number, if it does at all.
		 * this is due to huge inaccuracy calculating with such huge (or tiny) values that are of the plain type "Double".
		 */
		a = new Ultra(1, 2, 3, 0, 5, 0, 0, 0);
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());

		/**
		 * now exp() and ln() are tested, as well as pow():
		 */
		a = new Ultra(7, 5, 3, 2, 0, 0, 0, 0); // without dual
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());
		Assert.assertEquals(a, a.ln().exp());
		Assert.assertEquals(a, a.pow(a.inverse()).pow(a));
		
		a = new Ultra(7, 5, 0, 0, 3, 2, 0, 0); // without complex
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());
		Assert.assertEquals(a, a.ln().exp());
		Assert.assertEquals(a, a.pow(a.inverse()).pow(a));
		
		a = new Ultra(7, 0, 5, 0, 3, 0, 2, 0); // without binary
		Assert.assertEquals(a.plus(a), a.times(b));
		Assert.assertEquals(Ultra.ONE, a.by(a));
		Assert.assertEquals(a, a.inverse().inverse());
		Assert.assertEquals(a, a.ln().exp());
		Assert.assertEquals(a, a.pow(a.inverse()).pow(a));
		
		a = new Ultra(1, 0, 0, 0, 1, 1, 1, 1);
		Assert.assertEquals(a, a.ln().exp());
		Assert.assertEquals(a, a.pow(a.inverse()).pow(a));
		a = new Ultra(2, 1, 1, 1, 0, 0, 0, 0);
		Assert.assertEquals(a, a.ln().exp());
		Assert.assertEquals(a, a.pow(a.inverse()).pow(a));
		
		/**
		 * eulerian length is verified to work as with usual hyper-complex numbers:
		 */
		Hypercomplex test;
		test = new Complex(2, 1);
		Assert.assertEquals(test.eulerLength(), Math.exp(test.ln().re()));
		test = new Dual(2, 1);
		Assert.assertEquals(test.eulerLength(), Math.exp(test.ln().re()));
		test = new Binary(2, 1);
		Assert.assertEquals(test.eulerLength(), Math.exp(test.ln().re()));
		
		Assert.assertEquals(a.eulerLength(), Math.exp(a.ln().getDouble(0)));
		for (int i = 0; i < 8; ++i) {
			Assert.assertEquals(a.eulerLengthComponent(i), Math.exp(a.ln().getDouble(i)));
		}
		
		Ultra product = new Ultra(1);
		Ultra a2 = Ultra.unit(0).times(Math.log(a.eulerLengthComponent(0)));
		product = product.times(a2.exp());
		a2 = Ultra.unit(1).times(Math.log(a.eulerLengthComponent(1)));
		product = product.times(a2.exp());
		a2 = new Ultra();
		a2 = Ultra.unit(2).times(Math.log(a.eulerLengthComponent(2)));
		product = product.times(a2.exp());
		a2 = new Ultra();
		a2 = Ultra.unit(3).times(Math.log(a.eulerLengthComponent(3)));
		product = product.times(a2.exp());
		Assert.assertEquals(a, product);
		

		product = new Ultra(1);
		a2 = Ultra.unit(0).times(a.eulerAngleComponent(0));
		product = product.times(a2.exp());
		a2 = new Ultra();
		a2 = Ultra.unit(1).times(a.eulerAngleComponent(1));
		product = product.times(a2.exp());
		a2 = new Ultra();
		a2 = Ultra.unit(2).times(a.eulerAngleComponent(2));
		product = product.times(a2.exp());
		a2 = new Ultra();
		a2 = Ultra.unit(3).times(a.eulerAngleComponent(3));
		product = product.times(a2.exp());
		Assert.assertEquals(a, product);

		// sin/cos and asin/acos tested:
		a = new Ultra(0.1, 0.2, 0.3, 0, 0.5, 0, 0, 0);
		printTrig(a);
		Assert.assertEquals(a, a.asin().sin());
		Assert.assertEquals(a, a.acos().cos());
		//Assert.assertEquals(a, a.asec().sec());
		//Assert.assertEquals(a, a.acsc().csc());
		Assert.assertEquals(a, a.atan().tan());
		Assert.assertEquals(a, a.acot().cot());
		Assert.assertEquals(a, a.asinh().sinh());
		//Assert.assertEquals(a, a.acosh().cosh());
		Assert.assertEquals(a, a.asech().sech());
		Assert.assertEquals(a, a.acsch().csch());
		Assert.assertEquals(a, a.atanh().tanh());
		//Assert.assertEquals(a, a.acoth().coth());
		
		Assert.assertEquals(a, a.sin().asin());
		//Assert.assertEquals(a, a.cos().acos());
		//Assert.assertEquals(a, a.sec().asec());
		//Assert.assertEquals(a, a.csc().acsc());
		Assert.assertEquals(a, a.tan().atan());
		//Assert.assertEquals(a, a.cot().acot());
		Assert.assertEquals(a, a.sinh().asinh());
		//Assert.assertEquals(a, a.cosh().acosh());
		//Assert.assertEquals(a, a.sech().asech());
		//Assert.assertEquals(a, a.csch().acsch());
		//Assert.assertEquals(a, a.tanh().atanh());
		//Assert.assertEquals(a, a.coth().acoth());
		
		/*
		a = new Ultra(0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1);
		Assert.assertEquals(a, a.asin().sin());
		Assert.assertEquals(a, a.acos().cos());
		//Assert.assertEquals(a, a.asec().sec());
		//Assert.assertEquals(a, a.acsc().csc());
		Assert.assertEquals(a, a.atan().tan());
		Assert.assertEquals(a, a.acot().cot());
		Assert.assertEquals(a, a.asinh().sinh());
		//Assert.assertEquals(a, a.acosh().cosh());
		//Assert.assertEquals(a, a.asech().sech());
		//Assert.assertEquals(a, a.acsch().csch());
		//Assert.assertEquals(a, a.atanh().tanh());
		//Assert.assertEquals(a, a.acoth().coth());
		
		Assert.assertEquals(a, a.sin().asin());
		//Assert.assertEquals(a, a.cos().acos());
		//Assert.assertEquals(a, a.sec().asec());
		//Assert.assertEquals(a, a.csc().acsc());
		Assert.assertEquals(a, a.tan().atan());
		//Assert.assertEquals(a, a.cot().acot());
		Assert.assertEquals(a, a.sinh().asinh());
		//Assert.assertEquals(a, a.cosh().acosh());
		//Assert.assertEquals(a, a.sech().asech());
		//Assert.assertEquals(a, a.csch().acsch());
		//Assert.assertEquals(a, a.tanh().atanh());
		//Assert.assertEquals(a, a.coth().acoth());
		
		printTrig(a);
		*/
		a = new Ultra(0.1, 0, 0.1, 0, 0.1, 0, 0.1, 0);
		printTrig(a);
		Assert.assertEquals(a, a.asin().sin());
		Assert.assertEquals(a, a.acos().cos());
		Assert.assertEquals(a, a.asec().sec());
		Assert.assertEquals(a, a.acsc().csc());
		Assert.assertEquals(a, a.atan().tan());
		Assert.assertEquals(a, a.acot().cot());
		Assert.assertEquals(a, a.asinh().sinh());
		//Assert.assertEquals(a, a.acosh().cosh());
		Assert.assertEquals(a, a.asech().sech());
		Assert.assertEquals(a, a.acsch().csch());
		Assert.assertEquals(a, a.atanh().tanh());
		//Assert.assertEquals(a, a.acoth().coth());
		
		Assert.assertEquals(a, a.sin().asin());
		Assert.assertEquals(a, a.cos().acos());
		Assert.assertEquals(a, a.sec().asec());
		Assert.assertEquals(a, a.csc().acsc());
		Assert.assertEquals(a, a.tan().atan());
		//Assert.assertEquals(a, a.cot().acot());
		Assert.assertEquals(a, a.sinh().asinh());
		//Assert.assertEquals(a, a.cosh().acosh());
		Assert.assertEquals(a, a.sech().asech());
		Assert.assertEquals(a, a.csch().acsch());
		Assert.assertEquals(a, a.tanh().atanh());
		Assert.assertEquals(a, a.coth().acoth());

		a = new Ultra(2, 0, 0.1, 0, 0.1, 0, 0.1, 0);
		Assert.assertEquals(a, a.acosh().cosh());
		Assert.assertEquals(a, a.cosh().acosh());
		Assert.assertEquals(a, a.cot().acot());
		Assert.assertEquals(a, a.acoth().coth());
		
		
		double d = Math.PI / 16;
		a = new Ultra(d, d, d, d, d, d, d, d);
		printTrig(a);
		a = new Ultra(d, 0, d, 0, d, 0, d, 0); // without binary
		printTrig(a);
		a = new Ultra(d, d, 0, 0, d, d, 0, 0); // without complex
		printTrig(a);
		a = new Ultra(d, d, d, d, 0, 0, 0, 0); // without dual TODO: check csc, cot, coth; fix that type of bug in GENERAL
		printTrig(a);
		
	}
	
	public static void printTrig(Ultra x) {
		System.out.println("########################################");
		System.out.print("x: ");
		System.out.println(x);
		System.out.print("x.sin(): ");
		System.out.println(x.sin());
		System.out.print("x.cos(): ");
		System.out.println(x.cos());
		System.out.print("x.sec(): ");
		System.out.println(x.sec());
		System.out.print("x.csc(): ");
		System.out.println(x.csc());
		System.out.print("x.tan(): ");
		System.out.println(x.tan());
		System.out.print("x.cot(): ");
		System.out.println(x.cot());
		System.out.println();
		System.out.print("x.sinh(): ");
		System.out.println(x.sinh());
		System.out.print("x.cosh(): ");
		System.out.println(x.cosh());
		System.out.print("x.sech(): ");
		System.out.println(x.sech());
		System.out.print("x.csch(): ");
		System.out.println(x.csch());
		System.out.print("x.tanh(): ");
		System.out.println(x.tanh());
		System.out.print("x.coth(): ");
		System.out.println(x.coth());
		System.out.println();
		System.out.print("x.asin(): ");
		System.out.println(x.asin());
		System.out.print("x.acos(): ");
		System.out.println(x.acos());
		System.out.print("x.asec(): ");
		System.out.println(x.asec());
		System.out.print("x.acsc(): ");
		System.out.println(x.acsc());
		System.out.print("x.atan(): ");
		System.out.println(x.atan());
		System.out.print("x.acot(): ");
		System.out.println(x.acot());
		System.out.println();
		System.out.print("x.asinh(): ");
		System.out.println(x.asinh());
		System.out.print("x.acosh(): ");
		System.out.println(x.acosh());
		System.out.print("x.asech(): ");
		System.out.println(x.asech());
		System.out.print("x.acsch(): ");
		System.out.println(x.acsch());
		System.out.print("x.atanh(): ");
		System.out.println(x.atanh());
		System.out.print("x.acoth(): ");
		System.out.println(x.acoth());
		System.out.println();
		System.out.print("x.sin().asin(): ");
		System.out.println(x.sin().asin());
		System.out.print("x.cos().acos(): ");
		System.out.println(x.cos().acos());
		System.out.print("x.sec().asec(): ");
		System.out.println(x.sec().asec());
		System.out.print("x.csc().acsc(): ");
		System.out.println(x.csc().acsc());
		System.out.print("x.tan().atan(): ");
		System.out.println(x.tan().atan());
		System.out.print("x.cot().acot(): ");
		System.out.println(x.cot().acot());
		System.out.println();
		System.out.print("x.sinh().asinh(): ");
		System.out.println(x.sinh().asinh());
		System.out.print("x.cosh().acosh(): ");
		System.out.println(x.cosh().acosh());
		System.out.print("x.sech().asech(): ");
		System.out.println(x.sech().asech());
		System.out.print("x.csch().acsch(): ");
		System.out.println(x.csch().acsch());
		System.out.print("x.tanh().atanh(): ");
		System.out.println(x.tanh().atanh());
		System.out.print("x.coth().acoth(): ");
		System.out.println(x.coth().acoth());
		System.out.println();
		System.out.print("x.asin().sin(): ");
		System.out.println(x.asin().sin());
		System.out.print("x.acos().cos(): ");
		System.out.println(x.acos().cos());
		System.out.print("x.asec().sec(): ");
		System.out.println(x.asec().sec());
		System.out.print("x.acsc().csc(): ");
		System.out.println(x.acsc().csc());
		System.out.print("x.atan().tan(): ");
		System.out.println(x.atan().tan());
		System.out.print("x.acot().cot(): ");
		System.out.println(x.acot().cot());
		System.out.println();
		System.out.print("x.asinh().sinh(): ");
		System.out.println(x.asinh().sinh());
		System.out.print("x.acosh().cosh(): ");
		System.out.println(x.acosh().cosh());
		System.out.print("x.asech().sech(): ");
		System.out.println(x.asech().sech());
		System.out.print("x.acsch().csch(): ");
		System.out.println(x.acsch().csch());
		System.out.print("x.atanh().tanh(): ");
		System.out.println(x.atanh().tanh());
		System.out.print("x.acoth().coth(): ");
		System.out.println(x.acoth().coth());
	}
	
}
