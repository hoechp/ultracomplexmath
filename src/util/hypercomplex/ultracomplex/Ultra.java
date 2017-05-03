package util.hypercomplex.ultracomplex;

import java.util.ArrayList;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;

/**
 * I'd call these numbers ultra-complex numbers, because hyper-complex numbers have three
 * unique and special units sqrt(-1) == Ó, sqrt(1) ==   != 1, sqrt(0) == Í != 0
 * and when using them together, Ó , Í , ÍÓ, ÍÓ  also arise.
 * because of the possible M2R-definition of Ó,   and Í, you could think that
 * those arising units are really to be expressed as Ó,   or Í.
 * but since, for example, 1Ó  * 1Ó == -1  and 1Ó  * 1  == 1Ó,
 * those arising units are distinct different dimensions.
 * the Ó -dimension alone or with the real part can only behave like the Ó-dimension,
 * since (Ó )^2 == Ó^2 == -1. also (Í )^2 == (ÍÓ)^2 == (ÍÓ )^2 == Í^2 == 0,
 * so all dimensions with Í in it, when left alone or together with the real part, behave like the Í-dimension.
 * but as soon as multiple units are used together, they influence each other in their special ways.
 * <p>
 * complex numbers (Ó) can only do more than real numbers, because of the extension.
 * binary ( ) and dual (Í) numbers don't have all the features of complex numbers,
 * but also extend the real numbers in a way that's gaining features.
 * ultra-complex numbers unite all features of hypercomplex numbers.
 * but they also contain all restrictions, like there is no logarithm of (0 + x * Í) with x != 0,
 * also there's no logarithm of (a + b *  ) with b > a. and (a + b * Ó).exp() is periodic with 2 * PI * Ó,
 * and so on. all these restrictions must be obeyed when calculating ultra-complex computations.
 * though this way it can only fail by trying something that makes no sense.
 * otherwise restricted numbers can always arise in a context, where it makes sense.
 * so there's no logarithm of 1 + 2 , but it can be a solution of something with another meaning.
 * so in a way the natural restrictions are as helpful as the gained features.
 * <p>
 * very seldomly something that could be computed cannot be computed due to an insufficient implementation.
 * TODO: verify/fix that!
 * <p>
 * features<br>
 * - plus(addend), minus(subtrahend)<br>
 * - times(factor)<br>
 * - conjugate() and det() == determinant of corresponding minimal dimension (ultimately needed for inverse)<br>
 * - inverse(), by(divisor)<br>
 * - exp(), ln(), pow(exponent), log(base)<br>
 * - sin(), cos(), sec(), csc(), tan(), cot(), sinh(), cosh(), sech(), csch(), tanh(), coth()<br>
 * - asin(), acos(), asec(), acsc(), atan(), acot(), asinh(), acosh(), asech(), acsch(), atanh(), acoth()<br>
 * <p>
 * TODO: fix issues with trigonometry,
 *       maybe find better way to compute logarithm
 * @author hoechp
 *
 */
public class Ultra {
	
	private Component[] components;
	private static final int REUSE_LN = 2;
	public static final Ultra ONE = new Ultra(1, 0, 0, 0, 0, 0, 0, 0);
	public static final Ultra ZERO = new Ultra(0, 0, 0, 0, 0, 0, 0, 0);
	
	public static Ultra unit(int code) {
		if (code < -1 || code > 7) {
			return null;
		}
		double a[] = new double[8];
		for (int i = 0; i < 8; ++i) {
			if (code == i) {
				a[i] = 1;
			} else {
				a[i] = 0;
			}
		}
		return new Ultra(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]);
	}

	public Ultra() {
		components = new Component[8];
		for (int i = 0; i < 8; ++i) {
			components[i] = new Component(i, 0);
		}
	}
	
	public Ultra(Hypercomplex value) {
		components = new Component[8];
		for (int i = 0; i < 8; ++i) {
			components[i] = new Component(i, 0);
		}
		components[0] = new Component(0, value.re());
		if (value.isComplex()) {
			components[2] = new Component(2, value.im());
		}
		if (value.isDual()) {
			components[4] = new Component(4, value.im());
		}
		if (value.isBinary()) {
			components[1] = new Component(1, value.im());
		}
	}
	
	public Ultra(Ultra other) {
		components = new Component[8];
		for (int i = 0; i < 8; ++i) {
			components[i] = new Component(i, other.getComponent(i).getValue());
		}
	}
	
	public void set(Ultra other) {
		for (int i = 0; i < 8; ++i) {
			components[i] = new Component(i, other.getComponent(i).getValue());
		}
	}

	public Ultra(double a) {
		this(a, 0, 0, 0, 0, 0, 0, 0);
	}
	
	/**
	 * Contructor
	 * @param a real part
	 * @param b binary part
	 * @param c complex part
	 * @param d complex-binary part
	 * @param e dual part
	 * @param f dual-binary part
	 * @param g dual-complex part
	 * @param h dual-complex-binary part
	 */
	public Ultra(double a, double b, double c, double d, double e, double f, double g, double h) {
		components = new Component[8];
		components[0] = new Component(0, a);
		components[1] = new Component(1, b);
		components[2] = new Component(2, c);
		components[3] = new Component(3, d);
		components[4] = new Component(4, e);
		components[5] = new Component(5, f);
		components[6] = new Component(6, g);
		components[7] = new Component(7, h);
	}

	private void addComponent(Component add) {
		components[add.getType()].setValue(components[add.getType()].getValue().plus(add.getValue()));
	}
	
	private void setComponent(Component set) {
		components[set.getType()].setValue(set.getValue());
	}
	
	private Component getComponent(int code) {
		if (code < 0 || code > 7) {
			return null;
		}
		return components[code];
	}
	
	///////////////////////////////////////////////////////////////////////////////////////////
	
	public Ultra plus(Ultra other) {
		Ultra result = new Ultra();
		for (int i = 0; i < 8; ++i) {
			result.addComponent(getComponent(i));
			result.addComponent(other.getComponent(i));
		}
		return result;
	}
	
	public Ultra minus(Ultra other) {
		return plus(other.times(-1));
	}

	public Ultra times(Ultra other) {
		Ultra result = new Ultra();
		for (int i = 0; i < 8; ++i) { // components of this
			for (int j = 0; j < 8; ++j) { // components of other
				result.addComponent(getComponent(i).times(result, other.getComponent(j)));
			}
		}
		return result;
	}
	
	public Ultra times(double factor) {
		Ultra result = new Ultra();
		for (int i = 0; i < 8; ++i) {
			result.addComponent(new Component(i, getComponent(i).getValue().times(factor)));
		}
		return result;
	}
	
	public Ultra by(double devisor) {
		Ultra result = new Ultra();
		for (int i = 0; i < 8; ++i) {
			result.addComponent(new Component(i, getComponent(i).getValue().by(devisor)));
		}
		return result;
	}
	
	public Ultra conjugate() {
		ArrayList<Integer> nonZeroDimensions = new ArrayList<Integer>();
		for (int i = 1; i < 8; ++i) {
			if (!Complex.ZERO.equals(getComponent(i).getValue())) { // fixes conjugate() so it works with the minimal amount of dimensions
				nonZeroDimensions.add(i);
			}
		}
		int n = nonZeroDimensions.size() + 1;
		int factors = (int)(Math.pow(2, n - 1) - 1);
		ArrayList<Ultra> factorList = new ArrayList<Ultra>(); 
		for (int i = 1; i <= factors; ++i) {
			Ultra factor = new Ultra(getComponent(0).getValue().re());
			int number = i;
			for (int j = n - 1; j >= 1; --j) {
				int sign = (int)Math.pow(-1, number % 2);
				//System.out.print(number % 2);
				factor.setComponent(new Component(nonZeroDimensions.get(j - 1), getComponent(nonZeroDimensions.get(j - 1)).getValue().times(sign)));
				number /= 2;
			}
			//System.out.println(" -> " + factor);
			factorList.add(factor);
		}
		return multiplyWisely(factorList);
	}
	
	private Ultra multiplyWisely(ArrayList<Ultra> factorList) {
		factorList = multiplyFragments(factorList);
		Ultra product = new Ultra(ONE);
		for (Ultra u: factorList) {
			product = product.times(u);
		}
		return product;
	}
	
	private ArrayList<Ultra> multiplyFragments(ArrayList<Ultra> factorList) {
		ArrayList<Ultra> reducedList = new ArrayList<Ultra>();
		for (int i = 0; i < factorList.size(); i += 2) {
			if (i + 1 < factorList.size()) {
				reducedList.add(factorList.get(i).times(factorList.get(i + 1)));
			}
		}
		if (factorList.size() % 2 == 1) {
			reducedList.add(factorList.get(factorList.size() - 1));
		}
		if (reducedList.size() < 2) {
			return reducedList;
		} else {
			return multiplyFragments(reducedList);
		}
	}

	public double det() {
		return times(conjugate()).getDouble(0);
	}

	public Ultra inverse() {
		Ultra con = conjugate();
		return con.by(times(con).getDouble(0));
	}
	
	public Ultra by(Ultra devisor) {
		return times(devisor.inverse());
	}
	
	public Ultra exp() {
		// exp(x + y) = exp(x) * exp(y)
		ArrayList<Ultra> factorList = new ArrayList<Ultra>(); 
		for (int i = 0; i < 8; ++i) {
			Ultra factor = new Ultra();
			Hypercomplex expValue = getComponent(i).getValue().exp();
			factor.addComponent(new Component(0, expValue.re()));
			factor.addComponent(new Component(i, expValue.im()));
			factorList.add(factor);
		}
		return multiplyWisely(factorList);
	}
	
	/**
	 * eulerian length
	 * @return the eulerian length
	 */
	public double eulerLength() {
		return eulerLengthComponent(0);
	}
	
	/**
	 * take the logarithms from all of these values, multiply them with their bases,
	 * calculate exp() from those values, multiply the exp()s with each other
	 * and it will be the original value.<p>
	 * so its the eulerian value like the r in r * e^(phi * Ó)
	 * @param index the index of the component
	 * @return the corresponding eulerian component's double value
	 */
	public double eulerLengthComponent(int index) { // TODO: find out if its like multiple eulerAngle() values from single Hypercomplex
		return Math.exp(ln().getComponent(index).getDouble());
	}
	
	/**
	 * take all of these values, multiply them with their bases,
	 * calculate exp() from those values, multiply the exp()s with each other
	 * and it will be the original value.<p>
	 * so its the eulerian value like the phi in r * e^(phi * Ó)
	 * @param index the index of the component
	 * @return the corresponding eulerian component's double value
	 */
	public double eulerAngleComponent(int index) { // TODO: find out if its like multiple eulerAngle() values from single Hypercomplex
		return ln().getComponent(index).getDouble();
	}
	
	public double getDouble(int index) {
		return getComponent(index).getDouble();
	}
	
	/**
	 * cartesian length
	 * @return the cartesian length
	 */
	public double length() {
		double sum = 0;
		for (int i = 0; i < 8; ++i) {
			sum += Math.pow(getComponent(i).getDouble(), 2);
		}
		return Math.sqrt(sum);
	}
	
	private Ultra ln(int reuse, int steps) {
		/*
		 * ln(x * y) = ln(x) + ln(y)
		 * ln(x + y) = ln(x) + ln(1 + y / x)
		 * ln(x) = 2 * m * ln(sqrt(2)) + ln(2^(-m) * x)
		 * ln(x) = infinite sum from k = 0: 2 / (2 * k + 1) * ((x - 1)/(x + 1))^(2 * k + 1) // converges around 1
		 * 
		 * find ultra m with 2^(-m) * x near ONE:
		 * a^x == exp(x * ln(a))
		 * 2^-m * x == exp(-ln(2) * m) * x
		 * exp(-ln(2) * m) * x == 1
		 * exp(-ln(2) * m) == 1 / x
		 * ln(1 / x) == -ln(2) * m
		 * m == -ln(1 / x) / ln(2)
		 */
		Ultra m = new Ultra();
		if (reuse > 0) {
			m = inverse().ln(reuse - 1, steps).by(-Math.log(2));
		} else {
			m = inverse().ln2(REUSE_LN, steps).by(-Math.log(2));
		}
		/*
		 */
		Ultra sum = new Ultra(2 * Math.log(Math.sqrt(2))).times(m);
		Ultra restParameter = new Ultra(this).times(m.times(-Math.log(2)).exp());
		for (int k = 0; k < steps; ++k) {
			Ultra factor = new Ultra(ONE);
			Ultra originalFactor = new Ultra(restParameter).minus(ONE).by(new Ultra(restParameter).plus(ONE));
			for (int i = 1; i <= 2 * k + 1; ++i) {
				factor = factor.times(originalFactor);
			}
			sum = sum.plus(factor.times(2d / (2 * k + 1)));
		}
		return sum;
	}
	
	/*
	 * just good with values around real 1.
	 */
	private Ultra ln2(int reuse, int steps) {
		Ultra m = new Ultra();
		if (reuse > 0) {
			m = inverse().ln2(reuse - 1, steps).by(-Math.log(2));
		} else {
			m = new Ultra(Math.log(getComponent(0).getDouble()) / Math.log(2));
		}
		Ultra sum = new Ultra(2 * Math.log(Math.sqrt(2))).times(m);
		Ultra restParameter = new Ultra(this).times(m.times(-Math.log(2)).exp());
		for (int k = 0; k < steps; ++k) {
			Ultra factor = new Ultra(ONE);
			Ultra originalFactor = new Ultra(restParameter).minus(ONE).by(new Ultra(restParameter).plus(ONE));
			for (int i = 1; i <= 2 * k + 1; ++i) {
				factor = factor.times(originalFactor);
			}
			sum = sum.plus(factor.times(2 / (2 * k + 1)));
		}
		return sum;
	}

	/**
	 * natural logarithm. approximative.<p>
	 * the result + (m * 2 * PI * Ó + n * 2 * PI * Ó ), m,n out Z
	 * is a result again. similar to the usual complex principal value,
	 * here there are two of those additives, u can add or subtract as many times as u want (2 * PI * Ó AND 2 * PI * Ó ).
	 * @return the natural logarithm (principal value)
	 */
	public Ultra ln() {
		return ln(REUSE_LN, 1);
	}

	/**
	 * natural logarithm. approximative.
	 * @return the natural logarithm (principal value)
	 */
	public Ultra log(Ultra b) {
		return ln().by(b.ln());
	}


	/**
	 * power function.
	 * @param the exponent
	 * @return this number to the power of the given exponent.
	 */
	public Ultra pow(Ultra power) {
		// a^x == exp(x * ln(a))
		return ln().times(power).exp();
	}
	
	////////////////// trigonometry /////////////////////////////////
	// NORMAL - for all: periodic with 2 * PI AND 2 * PI *  
	/**
	 * sine<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return sine
	 */
	public Ultra sin() {
		// sin(x) = (exp(x * i) - exp(-x * i)) / (2 * i)
		Ultra i = new Ultra(Complex.I);
		return times(i).exp().minus(times(i).times(-1).exp()).by(i.times(2));
	}
	/**
	 * cosine<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return cosine
	 */
	public Ultra cos() {
		// sin(x) = (exp(x * i) + exp(-x * i)) / 2
		Ultra i = new Ultra(Complex.I);
		return times(i).exp().plus(times(i).times(-1).exp()).by(2);
	}
	/**
	 * secant<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return secant
	 */
	public Ultra sec() {
		return cos().inverse();
	}
	/**
	 * cosecant<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return cosecant
	 */
	public Ultra csc() {
		return sin().inverse();
	}
	/**
	 * tangent<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return tangent
	 */
	public Ultra tan() {
		return sin().by(cos());
	}
	/**
	 * cotangent<p>periodic with <b>2 * PI <u>and</u> 2 * PI *  </b>
	 * @return cotangent
	 */
	public Ultra cot() {
		return cos().by(sin());
	}
	// HYPERBOLIC
	/**
	 * hyperbolic sine
	 * @return hyperbolic sine
	 */
	public Ultra sinh() {
		// sinh(x) = (exp(x) - exp(-x)) / 2
		return exp().minus(times(-1).exp()).times(0.5);
	}
	/**
	 * hyperbolic cosine
	 * @return hyperbolic cosine
	 */
	public Ultra cosh() {
		// cosh(x) = (exp(x) + exp(-x)) / 2
		return exp().plus(times(-1).exp()).times(0.5);
	}
	/**
	 * hyperbolic secant
	 * @return hyperbolic secant
	 */
	public Ultra sech() {
		return cosh().inverse();
	}
	/**
	 * hyperbolic cosecant
	 * @return hyperbolic cosecant
	 */
	public Ultra csch() {
		return sinh().inverse();
	}
	/**
	 * hyperbolic tangent
	 * @return hyperbolic tangent
	 */
	public Ultra tanh() {
		return sinh().by(cosh());
	}
	/**
	 * hyperbolic cotangent
	 * @return hyperbolic cotangent
	 */
	public Ultra coth() {
		return cosh().by(sinh());
	}
	// INVERSE NORMAL - for all: principal value; add m * 2 * PI + n * 2 * PI *  , with m,n out Z, and it will be a result again.
	/**
	 * inverse sine<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse sine
	 */
	public Ultra asin() {
		// asin(x) = -i * ln(i * x + sqrt(1 - x^2))
		Ultra i = new Ultra(Complex.I);
		return times(i).plus(ONE.minus(times(this)).pow(ONE.by(2))).ln().times(i.times(-1));
	}
	/**
	 * inverse cosine<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse cosine
	 */
	public Ultra acos() {
		// acos(x) = -i * ln(x + i * sqrt(1 - x^2))
		Ultra i = new Ultra(Complex.I);
		return plus(ONE.minus(times(this)).pow(ONE.by(2)).times(i)).ln().times(i.times(-1));
	}
	/**
	 * inverse secant<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse secant
	 */
	public Ultra asec() {
		return inverse().acos();
	}
	/**
	 * inverse cosecant<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse cosecant
	 */
	public Ultra acsc() {
		return inverse().asin();
	}
	/**
	 * inverse tangent<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse tangent
	 */
	public Ultra atan() {
		// atan(x) = ((1 + i * x) / (1 - i * x)).ln() / (2 * i)
		Ultra i = new Ultra(Complex.I);
		return ONE.plus(times(i)).by(ONE.minus(times(i))).ln().by(i.times(2));
	}
	/**
	 * inverse cotangent<p>it's just the principal value. add<b><br>m * 2 * PI + n * 2 * PI *  ,<br>
	 * with m, n integer,</b><br>and it will be a result again.
	 * @return inverse cotangent
	 */
	public Ultra acot() {
		// acot(x) = PI/2 - atan(x)
		return ONE.times(Math.PI / 2).minus(atan());
	}
	// INVERSE HYPERBOLIC
	/**
	 * inverse hyperbolic sine
	 * @return inverse hyperbolic sine
	 */
	public Ultra asinh() {
		// asinh(x) = (x + sqrt(x^2 + 1)).ln()
		return plus(times(this).plus(ONE).pow(ONE.by(2))).ln();
	}
	/**
	 * inverse hyperbolic cosine
	 * @return inverse hyperbolic cosine
	 */
	public Ultra acosh() {
		// acosh(x) = (x + sqrt(x^2 - 1)).ln()
		return plus(times(this).minus(ONE).pow(ONE.by(2))).ln();
	}
	/**
	 * inverse hyperbolic secant
	 * @return inverse hyperbolic secant
	 */
	public Ultra asech() {
		// asech(x) = ((1 + sqrt(1 - x^2)) / x).ln()
		return ONE.plus(ONE.minus(times(this)).pow(ONE.by(2))).by(this).ln();
	}
	/**
	 * inverse hyperbolic cosecant
	 * @return inverse hyperbolic cosecant
	 */
	public Ultra acsch() {
		// acsch(x) = ((1 + sqrt(1 + x^2)) / x).ln()
		return ONE.plus(ONE.plus(times(this)).pow(ONE.by(2))).by(this).ln();
	}
	/**
	 * inverse hyperbolic tangent
	 * @return inverse hyperbolic tangent
	 */
	public Ultra atanh() {
		// atanh(x) = ((1 + x) / (1 - x)).ln() / 2
		return ONE.plus(this).by(ONE.minus(this)).ln().by(2);
	}
	/**
	 * inverse hyperbolic cotangent
	 * @return inverse hyperbolic cotangent
	 */
	public Ultra acoth() {
		// acoth(x) = ((x + 1) / (x - 1)).ln() / 2
		return plus(ONE).by(minus(ONE)).ln().by(2);
	}
	
	
	///////////////////////////////////////////////////////////////////////////////////////////
	
	public ArrayList<Ultra> nonZeroComponents() {
		ArrayList<Ultra> result = new ArrayList<Ultra>();
		for (int i = 0; i < 8; ++i) {
			if (getComponent(i).getDouble() != 0) {
				Ultra component = new Ultra();
				component.addComponent(new Component(i, getComponent(i).getDouble()));
				result.add(component);
			}
		}
		return result;
	}
	
	public boolean containsNaN() {
		for (int i = 0; i < 8; ++i) {
			if (((Double)(getComponent(i).getDouble())).isNaN()) {
				return true;
			}
		}
		return false;
	}
	
	///////////////////////////////////////////////////////////////////////////////////////////
	
	@Override
	public String toString() {
		if (containsNaN()) {
			return "" + Double.NaN;
		}
		String result = "";
		boolean first = true;
		for (int i = 0; i < 8; ++i) {
			if (!getComponent(i).getValue().toString().equals("0")) {
				if (!first) {
					result += " ";
				}
				first = false;
				result += getComponent(i).toStringSimple(i != 0);
			}
		}
		if (first) {
			return "0";
		}
		return result;
	}
	
	@Override
	public boolean equals(Object other) {
		boolean same = true;
		if (other instanceof Ultra) {
			for (int i = 0; i < 8; ++i) {
				if (!getComponent(i).equals(((Ultra)other).getComponent(i))) {
					same = false;
				}
			}
		} else {
			same = false;
		}
		return same;
	}
	
}
