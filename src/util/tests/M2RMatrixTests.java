package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.M2R;


public class M2RMatrixTests {

	@Test
	public void testInterdimensionalMultiplication() {
		// complex times dual -> (in this case) complex
		M2R test1 = new M2R(new Complex(1, 2));
		M2R test2 = new M2R(new Dual(5, 3));
		M2R result = test1.times(test2);
		M2R expected = new M2R(new Complex(8, Math.sqrt(61)));
		Assert.assertEquals(expected, result);
		test1 = new M2R(new Dual(5, 3));
		test2 = new M2R(new Complex(1, 2));
		result = test1.times(test2);
		expected = new M2R(new Complex(8, Math.sqrt(61)));
		Assert.assertEquals(expected, result);

		// complex times complex -> (obviously) complex
		test1 = new M2R(new Complex(1, 2));
		test2 = new M2R(new Complex(5, 3));
		result = test1.times(test2);
		expected = new M2R(new Complex(-1, 13));
		Assert.assertEquals(expected, result);
		Assert.assertEquals(test1, result.by(test2)); // reversible
		test1 = new M2R(new Complex(5, 3));
		test2 = new M2R(new Complex(1, 2));
		result = test1.times(test2);
		expected = new M2R(new Complex(-1, 13));
		Assert.assertEquals(expected, result);
		Assert.assertEquals(test1, result.by(test2)); // reversible

		// complex times dual -> binary positive idempotent
		test1 = new M2R(Complex.I);
		test2 = new M2R(Dual.I);
		result = test1.times(test2);
		expected = new M2R(Binary.IDEMPOTENT_POS);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(Dual.I);
		test2 = new M2R(Complex.I);
		result = test1.times(test2);
		expected = new M2R(Binary.IDEMPOTENT_POS);
		Assert.assertEquals(expected.value(), result.value());
		// complex times binary -> binary positive idempotent
		test1 = new M2R(Dual.I);
		test2 = new M2R(Binary.I);
		result = test1.times(test2);
		expected = new M2R(Binary.IDEMPOTENT_POS);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(Binary.I);
		test2 = new M2R(Dual.I);
		result = test1.times(test2);
		expected = new M2R(Binary.IDEMPOTENT_POS);
		Assert.assertEquals(expected.value(), result.value());
		// binary times complex -> binary
		test1 = new M2R(Binary.I);
		test2 = new M2R(Complex.I);
		result = test1.times(test2);
		expected = new M2R(Binary.I);
		Assert.assertEquals(expected.value(), result.value());
		Assert.assertEquals(test1.value(), result.by(test2).value()); // 'interdimensionally' reversible
		test1 = new M2R(Complex.I);
		test2 = new M2R(Binary.I);
		result = test1.times(test2);
		expected = new M2R(Binary.I);
		Assert.assertEquals(expected.value(), result.value());
		
		// dual times binary times complex -> dual times (-0.5)
		expected = new M2R(Dual.I.times(-0.5));
		test1 = new M2R(Dual.I);
		test2 = new M2R(Binary.I);
		result = test1.times(test2);
		test2 = new M2R(Complex.I);
		result = result.times(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(Binary.I);
		test2 = new M2R(Dual.I);
		result = test1.times(test2);
		test2 = new M2R(Complex.I);
		result = result.times(test2);
		Assert.assertEquals(expected.value(), result.value());

		// dual times complex times binary -> binary positive idempotent
		expected = new M2R(Binary.IDEMPOTENT_POS);
		test1 = new M2R(Dual.I);
		test2 = new M2R(Complex.I);
		result = test1.times(test2);
		test2 = new M2R(Binary.I);
		result = result.times(test2);
		test1 = new M2R(Complex.I);
		test2 = new M2R(Dual.I);
		result = test1.times(test2);
		test2 = new M2R(Binary.I);
		result = result.times(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(Complex.I);
		test2 = new M2R(Binary.I);
		result = test1.times(test2);
		test2 = new M2R(Dual.I);
		result = result.times(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(Binary.I);
		test2 = new M2R(Complex.I);
		result = test1.times(test2);
		test2 = new M2R(Dual.I);
		result = result.times(test2);
		Assert.assertEquals(expected.value(), result.value());
	}

	@Test
	public void testInterdimensionalAddition() {
		// (1 + 2X)(5 + 3Y) with different hyper-complex X, Y
		M2R test1 = new M2R(new Complex(1, 2));
		M2R test2 = new M2R(new Dual(5, 3));
		M2R result = test1.plus(test2);
		M2R expected = new M2R(new Binary(6, Math.sqrt(2)));
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Dual(5, 3));
		test2 = new M2R(new Complex(1, 2));
		result = test1.plus(test2);
		expected = new M2R(new Binary(6, Math.sqrt(2)));
		Assert.assertEquals(expected.value(), result.value());

		test1 = new M2R(new Dual(1, 2));
		test2 = new M2R(new Binary(5, 3));
		result = test1.plus(test2);
		expected = new M2R(new Binary(6, Math.sqrt(15)));
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Binary(5, 3));
		test2 = new M2R(new Dual(1, 2));
		result = test1.plus(test2);
		expected = new M2R(new Binary(6, Math.sqrt(15)));
		Assert.assertEquals(expected.value(), result.value());

		test1 = new M2R(new Binary(1, 2));
		test2 = new M2R(new Complex(5, 3));
		result = test1.plus(test2);
		expected = new M2R(new Complex(6, Math.sqrt(5)));
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Complex(5, 3));
		test2 = new M2R(new Binary(1, 2));
		result = test1.plus(test2);
		expected = new M2R(new Complex(6, Math.sqrt(5)));
		Assert.assertEquals(expected.value(), result.value());

		// within the same algebra associativity is preserved
		test1 = new M2R(new Complex(1, 2));
		test2 = new M2R(new Complex(5, 3));
		result = test1.plus(test2);
		expected = new M2R(new Complex(6, 5));
		Assert.assertEquals(expected.value(), result.value());
		Assert.assertEquals(test1.value(), result.minus(test2).value()); // reversible
		test1 = new M2R(new Complex(5, 3));
		test2 = new M2R(new Complex(1, 2));
		result = test1.plus(test2);
		expected = new M2R(new Complex(6, 5));
		Assert.assertEquals(expected.value(), result.value());
		Assert.assertEquals(test1.value(), result.minus(test2).value()); // reversible

		// two of three imaginary units added
		test1 = new M2R(new Binary(0, 1));
		test2 = new M2R(new Complex(0, 1));
		result = test1.plus(test2);
		expected = new M2R(new Dual(0, 2));
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Complex(0, 1));
		test2 = new M2R(new Dual(0, 1));
		result = test1.plus(test2);
		expected = new M2R(new Dual(0, 1));
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Dual(0, 1));
		test2 = new M2R(new Binary(0, 1));
		result = test1.plus(test2);
		expected = new M2R(new Binary(0, Math.sqrt(2)));
		Assert.assertEquals(expected.value(), result.value());

		// all three imaginary units added in different orders
		expected = new M2R(new Binary(0, 1));
		test1 = new M2R(new Dual(0, 1));
		test2 = new M2R(new Binary(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Complex(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Binary(0, 1));
		test2 = new M2R(new Dual(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Complex(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());

		expected = new M2R(new Binary(0, Math.sqrt(2)));
		test1 = new M2R(new Dual(0, 1));
		test2 = new M2R(new Complex(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Binary(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Complex(0, 1));
		test2 = new M2R(new Dual(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Binary(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());

		expected = new M2R(new Dual(0, 3));
		test1 = new M2R(new Complex(0, 1));
		test2 = new M2R(new Binary(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Dual(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());
		test1 = new M2R(new Binary(0, 1));
		test2 = new M2R(new Complex(0, 1));
		result = test1.plus(test2);
		test2 = new M2R(new Dual(0, 1));
		result = result.plus(test2);
		Assert.assertEquals(expected.value(), result.value());
	}
	
	@Test
	public void testPow() {
		/* test if a hyper-complex number from each algebra to the power of
		 * another hyper-complex number from the same algebra is correct
		 */
		M2R test1 = new M2R(new Complex(2, 1));
		M2R test2 = new M2R(new Complex(5, 3));
		M2R expected = new M2R(test1.value().pow(test2.value()));
		M2R result = test1.pow(test2);
		Assert.assertEquals(expected, result);

		test1 = new M2R(new Dual(2, 1));
		test2 = new M2R(new Dual(5, 3));
		expected = new M2R(test1.value().pow(test2.value()));
		result = test1.pow(test2);
		Assert.assertEquals(expected, result);

		test1 = new M2R(new Binary(2, 1));
		test2 = new M2R(new Binary(5, 3));
		expected = new M2R(test1.value().pow(test2.value()));
		result = test1.pow(test2);
		Assert.assertEquals(expected, result);
	}
	
}
