package util.hypercomplex;


import java.awt.Color;
import java.util.ArrayList;
import java.util.Vector;




import util.basics.Vectors;
import util.hypercomplex.calculation.Calculation;
import util.hypercomplex.simpleCalculation.SimpleCalculation;
import util.tests.Tests;

/**
 * A hyper-complex number (complex, binary or dual).<p>
 * 
 * It extends Number and implements Comparable&ltNumber&gt and Cloneable.
 * It also overwrites equals(Number other) and toString().<p>
 * 
 * About all functions you could think of are implemented like from addition, subtraction over
 * exponential function, roots, logarithms, all hyper-complex trigonometric functions
 * and the hyperbolic versions and their inverses to functions to determine if a number is one
 * of an infinite number of solutions to - lets say - a logarithm or a complex number to the power of another.<p>
 * 
 * Some functions are specific to just complex, binary or dual numbers - since they can be interpreted in different ways.
 * 
 * @see Number
 * @see Comparable
 * @see Cloneable
 * @author Philipp Kolodziej
 */
abstract public class Hypercomplex extends Number implements Comparable<Number>, Cloneable {

	// ------------------------- PRIVATE FIELD DATA -------------------------

	private boolean complex = false;
	private boolean binary = false;
	private boolean dual = false;

	/**
	 * serial version id
	 */
	private static final long serialVersionUID = -7717000598475609597L;

	/**
	 * the cartesian version of this vector.
	 */
	private Cartesian2D cartVec = null;

	/**
	 * the polynominal version of this vector.
	 */
	private Polynominal2D polVec = null;

	// ------------------------- STATIC INTERFACE (CONSTANTS) -------------------------
	
	/**
	 * the number of max ciphers (after decimal point) to be displayed per number
	 */
	public final static int DISPLAYED_CIPHER_COUNT = 8;

	// ------------------------- NON-STATIC INTERFACE (CONSTRUCTORS) -------------------------
	
	/**
	 * Constructor. Constructs a hyper-complex number containing the provided parsable data.
	 * @param parseData the String-representation of the number
	 */
	protected Hypercomplex(String parseData) {
		setCartesian(parseHypercomplex(parseData).getCartesian());
	}
	
	/**
	 * constructor. constructs a vector containing the cartesian and polynominal values (0, 0).
	 */
	protected Hypercomplex() {
		setPolynominal(0, 0);
	}

	/**
	 * Constructor. Constructs a real complex number containing the provided real value.
	 * @param re the real part
	 */
	protected Hypercomplex(double re) {
		setCartesian(re, 0);
	}

	/**
	 * Constructor. Constructs a complex number containing the provided values.<br>
	 * <b>Note</b> the provided values will be treated as cartesian values.
	 * @param re the real part
	 * @param im the imaginary part
	 */
	protected Hypercomplex(double re, double im) {
		setCartesian(re, im);
	}

	/**
	 * Constructor. Constructs a complex number containing the provided values.<br>
	 * Use format == "p" or "P" and the values will be treated as polynominal.
	 * Use format == "c" or "C" and the values will be treated as cartesian.
	 * @param r the length or real part
	 * @param phi the angle or imaginary part
	 */
	protected Hypercomplex(String format, double r, double phi) {
		if (format.equals("c") || format.equals("C")) {
			setCartesian(r, phi);
		} else if (format.equals("p") || format.equals("P")) {
			setPolynominal(r, phi);
		} else {
			setCartesian(Double.NaN, Double.NaN);
		}
	}

	/**
	 * Parses a hyper-complex number from its representation as in Hypercomplex.toString().<br>
	 * Also parsed are any kind of calculational expressions as allowed with calculation.Operator.<p>
	 * 
	 * parsable examples:<br>
	 * "1", "î", "3.1î", "3.1*î", "1 + î", "pi + eî", "1e-2 + 1e5î", "cos(1/2*phi) + tan(pi)î", "sqrt(-1)" == î, ...<br>
	 * @see util.hypercomplex.Hypercomplex.toString()
	 * @param expression the hyper-complex number as a string
	 * @return the hyper-complex number as a Hypercomplex
	 */
	public static Hypercomplex parseHypercomplex(String expression) {
		return new SimpleCalculation(expression).result(); // TODO: check if ok - had to be simplified cuz new Calculation(str).result() now parsed Ultra
	}
	
	/**
	 * Better use the usual Hypercomplex.parseHypercomplex(String expression) if possible!<p>
	 * Parses a hyper-complex number from its representation as in Hypercomplex.toString().<br>
	 * Also parsed are any kind of calculational expressions as allowed with calculation.Operator.<br>
	 * Only extra rules:<br>
	 * - if the imaginary unit is used it can only be the very last character,
	 * if both parts are used the beginning of the imaginary part is marked by a " +" or " -".
	 * between there (or the beginning) and the imaginary character is the imaginary part<br>
	 * <br>
	 * parsable examples:<br>
	 * "1", "î", "3.1î", "3.1*î", "1 + î", "pi + eî", "1e-2 + 1e5î", "cos(1/2*phi) + tan(pi)î"<br>
	 * <br>
	 * ununsual behaviour:<br>
	 * "1 - 1+1î" is interpreted as "1 -( 1+1)î" not as "(1 - 1)+1î" - the brackets are implicit<br>
	 * "1+ 1î" is interpreted as "(1+ 1)î" not as "1+ (1î)" - if the whitespace is missing the brackets are implicit<br>
	 * but "1 + 1î" is interpreted as "1 +( 1î) since it has the whitespace it needs and the implicit brackets are ok<br>
	 * @see util.hypercomplex.Hypercomplex.toString()
	 * @param expression the hyper-complex number as a string
	 * @return the hyper-complex number as a Hypercomplex
	 */
	public static Hypercomplex parseHypercomplexWeak(String expression) {
		if (expression.length() < 1) {
			return new Complex(Double.NaN);
		}
		if (expression != null) {
			if (expression.startsWith("+ ")) {
				expression = "+" + expression.substring(2);
			}
			if (expression.startsWith("- ")) {
				expression = "-" + expression.substring(2);
			}
		}
		if (expression.trim().contains(" -") || expression.trim().contains(" +")) {
			String split = " +";
			String split2 = " -";
			int index = Math.max(expression.lastIndexOf(split), expression.lastIndexOf(split2));
			String first = expression.substring(0, index).trim();
			Double value1 = parseDouble(first);
			Double value2 = null;
			char signature = '\0';
			if (expression.contains("+î") || expression.contains("-î")
					|| expression.contains("+Ê") || expression.contains("-Ê")
					|| expression.contains("+ê") || expression.contains("-ê")) {
				if (expression.contains("+î") || expression.contains("+Ê") || expression.contains("+ê")) {
					value2 = 1d;
				} else {
					value2 = -1d;
				}
				if (expression.contains("î")) {
					signature = 'î';
				} else if (expression.contains("Ê")) {
					signature = 'Ê';
				} else {
					signature = 'ê';
				}
			} else {
				String second = expression.substring(index).trim();
				signature = second.charAt(second.length() - 1);
				second = second.substring(0, second.length() - 1).trim();
				if (second.endsWith("*")) {
					second = second.substring(0, second.length() - 1);
				}
				if (second.trim().equals("-")) {
					second = "-1d";
				}
				if (second.trim().equals("+")) {
					second = "1d";
				}
				if (second.trim().equals("")) {
					second = "1d";
				}
				if (second.startsWith("+ ")) {
					second = "+" + second.substring(2);
				}
				if (second.startsWith("- ")) {
					second = "-" + second.substring(2);
				}
				value2 = parseDouble(second);
			}
			
			switch (signature) {
			case 'î':
				return new Complex(value1, value2);
			case 'Ê':
				return new Binary(value1, value2);
			case 'ê':
				return new Dual(value1, value2);
			default:
				return null;
			}
		} else if (expression.contains("î") || expression.contains("Ê") || expression.contains("ê")) {
			char signature = expression.trim().charAt(expression.trim().length() - 1);
			expression = expression.trim().substring(0, expression.trim().length() - 1);
			if (expression.endsWith("*")) {
				expression = expression.substring(0, expression.length() - 1);
			}
			Double value = null;
			if (expression.trim().length() == 0) {
				value = 1d;
			} else if (expression.trim().length() == 1) {
				if (expression.trim().charAt(0) == '+') {
					value = 1d;
				} else if (expression.trim().charAt(0) == '-') {
					value = -1d;
				} else {
					value = parseDouble(expression);
				}
			} else {
				value = parseDouble(expression);
			}
			switch (signature) {
			case 'î':
				return new Complex(0, value);
			case 'Ê':
				return new Binary(0, value);
			case 'ê':
				return new Dual(0, value);
			default:
				return null;
			}
		} else {
			expression = expression.trim();
			if (expression.startsWith("+ ")) {
				expression = "+" + expression.substring(2);
			}
			if (expression.startsWith("- ")) {
				expression = "-" + expression.substring(2);
			}
			return new Complex(parseDouble(expression));
		}
	}
	
	/**
	 * only parsed a number thats parsable by parseDouble()
	 * or the same but followed by î, ê or Ê to indicate to be some kind of hyper-complex.
	 * @param expression the expression to parse
	 * @return the parsed hyper-complex (pure real or pure imaginary) number
	 */
	public static Hypercomplex parseHypercomplexWeakest(String expression) {
		expression = expression.trim();
		double value = Double.NaN;
		if (expression.endsWith("î")) {
			expression = expression.substring(0, expression.length() - 1);
			if ("".equals(expression)) {
				expression = "1";
			}
			if (expression.endsWith("*")) {
				expression = expression.substring(0, expression.length() - 1);
			}
			value = parseDoubleWeak(expression);
			return new Complex(0, value);
		}
		if (expression.endsWith("ê")) {
			expression = expression.substring(0, expression.length() - 1);
			if ("".equals(expression)) {
				expression = "1";
			}
			if (expression.endsWith("*")) {
				expression = expression.substring(0, expression.length() - 1);
			}
			value = parseDoubleWeak(expression);
			return new Dual(0, value);
		}
		if (expression.endsWith("Ê")) {
			expression = expression.substring(0, expression.length() - 1);
			if ("".equals(expression)) {
				expression = "1";
			}
			if (expression.endsWith("*")) {
				expression = expression.substring(0, expression.length() - 1);
			}
			value = parseDoubleWeak(expression);
			return new Binary(0, value);
		}
		value = parseDoubleWeak(expression);
		return new Complex(value);
	}
	
	public static double parseDouble(String str) {
		double toParse = Double.NaN;
		try {
			toParse = Double.parseDouble(str);
		} catch (NumberFormatException e1) {
			try {
				toParse = recognizeConstant(str);
			} catch (NumberFormatException e2) {
				try {
					Hypercomplex result = new SimpleCalculation(str).result(); // TODO: check if ok - had to be simplified cuz new Calculation(str).result() now parsed Ultra
					if (result.isReal()) {
						return result.re();
					}
					throw new NumberFormatException(str);
				} catch (Throwable t) {
					throw new NumberFormatException(str);
				}
			}
		}
		return toParse;
	}
	
	private static double parseDoubleWeak(String str) {
		double toParse = Double.NaN;
		try {
			toParse = Double.parseDouble(str);
		} catch (NumberFormatException e1) {
			toParse = recognizeConstant(str);
		}
		return toParse;
	}

	private static double recognizeConstant(String str) {
		if (str.toLowerCase().equals("e")) {
			return Math.E;
		}
		if (str.toLowerCase().equals("pi")) {
			return Math.PI;
		}
		throw new NumberFormatException(str);
	}
	
	// ------------------------- hyper-complex 3D-angles (like usual: around z, measured from x) -------------------------
	

	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Complex angle), length)<br>
	 * the corresponding Complex angle is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured Complex angle
	 */
	public static Complex complex3DAngle(Vector<Double> vector) {
		// normalize (3D complex angle normalization)
		vector = Vectors.by(vector, complex3DLength(vector));
		// determine real part of angle
		Complex angleTest = new Complex(vector.get(0), vector.get(1));
		// recognize complex part of angle from 3D vector length and z-direction
		double length = Vectors.length(vector);
		double imPhi = (Hypercomplex.asinh(vector.get(2)) < 0 ? -1 : 1) * Hypercomplex.asinh(Math.sqrt((Math.pow(length, 2) - 1) / 2));
		// return result
		return new Complex(angleTest.phi(), imPhi);
	}

	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Dual angle), length)<br>
	 * the corresponding Dual angle is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured Dual angle
	 */
	public static Dual dual3DAngle(Vector<Double> vector) {
		// normalize (3D dual angle normalization)
		vector = Vectors.by(vector, dual3DLength(vector));
		// determine real part of angle
		Complex angleTest = new Complex(vector.get(0), vector.get(1));
		// recognize dual part of angle from 3D vector length and z-direction
		double imPhi = Math.sqrt(Math.pow(Vectors.length(vector), 2) - 1);
		boolean posZ = vector.get(2) < 0;
		if (posZ) {
			imPhi *= -1;
		}
		// return result
		return new Dual(angleTest.phi(), imPhi);
	}
	
	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Binary angle), length)<br>
	 * the corresponding Binary angle is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis<p>
	 * notorious 'problem': +-(2 * k + 1) * PI for angle1 means +-(2 * m + 1) * PI for angle2.
	 * or in other words: if angle1 is turned by 180° and angle2 too, then it's the same result.
	 * so this function could always for example return PI less at the real part and PI more at the imaginary part,
	 * or the other way around, or PI more for both parts, or PI less for both parts, or the result you'd expect.
	 * obviously that is since normal trigonometric angles are periodic with 2 * PI
	 * and each angle inverts the whole result when turned by PI or 180°.
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured Binary angle
	 */
	public static Binary binary3DAngle(Vector<Double> vector) {
		// normalize (3D binary angle normalization)
		vector = Vectors.by(vector, binary3DLength(vector));
		// determine real part of angle
		double re = new Complex(vector.get(0), vector.get(1)).phi();
		// 'project away' the real angle and save in Vector<Double> proj
		Complex helper = new Complex(re, 0);
		Vector<Double> helperV = Vectors.vectorFromHypercomplexAngle(helper);
		Vector<Double> z = Vectors.base3D().get(2);
		@SuppressWarnings("unchecked")
		Vector<Double> proj = Vectors.fromBase(vector, helperV, Vectors.cross(helperV, z), z);
		// read the projection to determine the binary part of the angle and return result
		return new Binary(re, new Complex(proj.get(0), proj.get(2)).phi());
	}

	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Complex angle), length)<br>
	 * the corresponding double length is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured complex 3D angle-length
	 */
	public static double complex3DLength(Vector<Double> vector) {
		double length2D = Math.sqrt(Math.pow(vector.get(0), 2) + Math.pow(vector.get(1), 2));
		Binary hyperbolicTest = new Binary(length2D, Math.abs(vector.get(2)));
		return hyperbolicTest.eulerLength();
	}

	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Dual angle), length)<br>
	 * the corresponding double length is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured dual 3D angle-length
	 */
	public static double dual3DLength(Vector<Double> vector) {
		return Math.sqrt(Math.pow(vector.get(0), 2) + Math.pow(vector.get(1), 2));
	}

	/**
	 * vector is interpreted as Vectors.times(Vectors.vectorFromHypercomplexAngle(Binary angle), length)<br>
	 * the corresponding double length is being returned.<p>
	 * the z-axis of the vector is interpreted as the combined imaginary part from the real x-axis and real y-axis
	 * @see Vectors.vectorFromHypercomplexAngle(Hypercomplex)
	 * @param vector the vector to be measured
	 * @return the measured binary 3D angle-length
	 */
	public static double binary3DLength(Vector<Double> vector) {
		return Vectors.length(vector);
	}
	

	// ------------------------- PRIVATE SETTER -------------------------

	/**
	 * Set the vector with cartesian parameters.
	 * @param cart the cartesian vector
	 */
	protected void setCartesian(Cartesian2D cart) {
		if (cartVec == null) {
			cartVec = new Cartesian2D();
		}
		cartVec.set(0, cart.get(0));
		cartVec.set(1, cart.get(1));
		polVec = cartVec.getPolynominal();
	}

	// ------------------------- NON-STATIC INTERFACE (VALUE SETTING) -------------------------
	
	/**
	 * Copies the values of the given vector into this vector.
	 * @param original the vector that is to copy
	 */
	public void set(Hypercomplex original) {
		setCartesian(original.getCartesian());
	}

	/**
	 * Set the vector with cartesian parameters.
	 * @param x the x ordinate of the vector
	 * @param y the y ordinate of the vector
	 */
	public void setCartesian(double x, double y) {
		if (cartVec == null) {
			cartVec = new Cartesian2D();
		}
		cartVec.set(0, x);
		cartVec.set(1, y);
		polVec = cartVec.getPolynominal();
	}

	/**
	 * Set the vector with polynominal parameters.
	 * @param r the length of the vector
	 * @param phi the angle of the vector
	 */
	public void setPolynominal(double r, double phi) {
		if (polVec == null) {
			polVec = new Polynominal2D();
		}
		polVec.set(0, r);
		polVec.set(1, phi);
		polVec.checkDirectionAndAngle();
		cartVec = polVec.getCartesian();
	}

	/**
	 * Set the real part of this complex number.
	 * @param real the real part
	 */
	public void setReal(double real) {
		setCartesian(real, im());
	}

	/**
	 * Set the imaginary part of this complex number.
	 * @param imaginary the real part
	 */
	public void setImaginary(double imaginary) {
		setCartesian(re(), imaginary);
	}

	/**
	 * Set the length of this complex number.
	 * @param r the length
	 */
	public void setR(double r) {
		setPolynominal(r, phi());
	}

	/**
	 * Set the angle of this complex number.
	 * @param phi the angle
	 */
	public void setPhi(double phi) {
		setPolynominal(r(), phi);
	}

	// ------------------------- NON-STATIC INTERFACE (COMPLEX CALCULATION) -------------------------

	/**
	 * Returns a vector that is the sum of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the sum of this vector and the given vector
	 */
	public Hypercomplex plus(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).plus(other);
		}
		if (isBinary()) {
			return ((Binary)this).plus(other);
		}
		if (isDual()) {
			return ((Dual)this).plus(other);
		}
		return null;
	}

	/**
	 * Returns a vector that is the difference of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the difference of this vector and the given vector
	 */
	public Hypercomplex minus(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).minus(other);
		}
		if (isBinary()) {
			return ((Binary)this).minus(other);
		}
		if (isDual()) {
			return ((Dual)this).minus(other);
		}
		return null;
	}

	/**
	 * Returns a vector that is the product of this vector and the given factor.
	 * @param factor the factor
	 * @return a vector that is the product of this vector and the given factor
	 */
	public Hypercomplex times(double factor) {
		if (isComplex()) {
			return ((Complex)this).times(factor);
		}
		if (isBinary()) {
			return ((Binary)this).times(factor);
		}
		if (isDual()) {
			return ((Dual)this).times(factor);
		}
		return null;
	}

	/**
	 * Returns a vector that is the quotient of this vector and the given divisor.
	 * @param divisor the divisor
	 * @return a vector that is the quotient of this vector and the given divisor
	 */
	public Hypercomplex by(double divisor) {
		if (isComplex()) {
			return ((Complex)this).by(divisor);
		}
		if (isBinary()) {
			return ((Binary)this).by(divisor);
		}
		if (isDual()) {
			return ((Dual)this).by(divisor);
		}
		return null;
	}

	/**
	 * Returns a complex number that is the (complex) product of this complex number and the given complex factor.
	 * @param f the (complex) factor
	 * @return a complex number that is the (complex) product of this complex number and the given complex factor
	 */
	public Hypercomplex times(Hypercomplex f) {
		if (isComplex()) {
			return ((Complex)this).times(f);
		}
		if (isBinary()) {
			return ((Binary)this).times(f);
		}
		if (isDual()) {
			return ((Dual)this).times(f);
		}
		return null;
	}

	/**
	 * Returns a complex number that is the (complex) quotient of this complex number and the given complex divisor.
	 * @param d the (complex) divisor
	 * @return a complex number that is the (complex) quotient of this complex number and the given complex divisor
	 */
	public Hypercomplex by(Hypercomplex d) {
		if (isComplex()) {
			return ((Complex)this).by(d);
		}
		if (isBinary()) {
			return ((Binary)this).by(d);
		}
		if (isDual()) {
			return ((Dual)this).by(d);
		}
		return null;
	}

	/**
	 * Returns a complex number that is the (complex) inverse of this complex number.
	 * @return a complex number that is the (complex) inverse of this complex number
	 */
	public Hypercomplex inverse() {
		if (isComplex()) {
			return ((Complex)this).inverse();
		}
		if (isBinary()) {
			return ((Binary)this).inverse();
		}
		if (isDual()) {
			return ((Dual)this).inverse();
		}
		return null;
	}

	/**
	 * Returns a complex number that is the complex conjugate of this complex number.
	 * @return a complex number that is the complex conjugate of this complex number
	 */
	public Hypercomplex conjugate() {
		if (isComplex()) {
			return ((Complex)this).conjugate();
		}
		if (isBinary()) {
			return ((Binary)this).conjugate();
		}
		if (isDual()) {
			return ((Dual)this).conjugate();
		}
		return null;
	}

	/**
	 * Returns an ArrayList of the n complex numbers that are the n-th roots of this complex number.
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return an ArrayList of the n complex numbers that are the n-th roots of this complex number
	 */
	public ArrayList<? extends Hypercomplex> roots(int n) {
		if (isComplex()) {
			return ((Complex)this).roots(n);
		}
		if (isBinary()) {
			return ((Binary)this).roots(n);
		}
		if (isDual()) {
			return ((Dual)this).roots(n);
		}
		return null;
	}

	/**
	 * Returns an ArrayList of the n complex numbers that are this to the power of (a / n).
	 * @param a the numerator
	 * @param n the denominator
	 * @return an ArrayList of the n complex numbers that are this to the power of (a / n)
	 */
	public ArrayList<? extends Hypercomplex> pow(int a, int n) {
		if (isComplex()) {
			return ((Complex)this).pow(a, n);
		}
		if (isBinary()) {
			return ((Binary)this).pow(a, n);
		}
		if (isDual()) {
			return ((Dual)this).pow(a, n);
		}
		return null;
	}
	
	/**
	 * Returns a complex number that is this complex number to the power p.
	 * @param p the power
	 * @return a complex number that is this complex number to the power p
	 */
	public Hypercomplex pow(double p) {
		if (isComplex()) {
			return ((Complex)this).pow(p);
		}
		if (isBinary()) {
			return ((Binary)this).pow(p);
		}
		if (isDual()) {
			return ((Dual)this).pow(p);
		}
		return null;
	}
	
	/**
	 * Returns the principal value of e to the power of this complex number.
	 * @return the principal value of e to the power of this complex number
	 */
	public Hypercomplex exp() {
		if (isComplex()) {
			return ((Complex)this).exp();
		}
		if (isBinary()) {
			return ((Binary)this).exp();
		}
		if (isDual()) {
			return ((Dual)this).exp();
		}
		return null;
	}
	
	/**
	 * Returns the principal natural logarithm of this complex number.
	 * @return the principal natural logarithm of this complex number
	 */
	public Hypercomplex ln() {
		if (isComplex()) {
			return ((Complex)this).ln();
		}
		if (isBinary()) {
			return ((Binary)this).ln();
		}
		if (isDual()) {
			return ((Dual)this).ln();
		}
		return null;
	}
	
	/**
	 * Complex logarithm (principal value) of this to the base of b.
	 * Returns log_b(this) with b being the complex base.
	 * @param b the complex base
	 * @return log_b(this) with b being the complex base
	 */
	public Hypercomplex log(Hypercomplex b) {
		if (isComplex()) {
			return ((Complex)this).log(b);
		}
		if (isBinary()) {
			return ((Binary)this).log(b);
		}
		if (isDual()) {
			return ((Dual)this).log(b);
		}
		return null;
	}
	
	/**
	 * Returns the principal value of this complex number to the power of the other provided complex exponent.
	 * @param w the complex exponent
	 * @return the principal value of this complex number to the power of the other provided complex exponent
	 */
	public Hypercomplex pow(Hypercomplex w) { // z^w = exp(log(z) * w) = exp(a) * exp(b * i)
		if (isComplex()) {
			return ((Complex)this).pow(w);
		}
		if (isBinary()) {
			return ((Binary)this).pow(w);
		}
		if (isDual()) {
			return ((Dual)this).pow(w);
		}
		return null;
	}

	// ------------------------- NON-STATIC INTERFACE (TESTING COMPLEX NUMBERS) -------------------------

	/**
	 * Returns true if this complex number is a (one of an infinite number) natural logarithm of the other complex number
	 * @param other the other complex number
	 * @return true if this complex number is a (one of an infinite number) natural logarithm of the other complex number, otherwise false
	 */
	public boolean isLn(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).isLn(other);
		}
		if (isBinary()) {
			return ((Binary)this).isLn(other);
		}
		if (isDual()) {
			return ((Dual)this).isLn(other);
		}
		return false;
	}

	/**
	 * Returns true if this complex number is a (of an infinite number)
	 * logarithm to the provided base of the other complex number
	 * @param base the complex base
	 * @param other the other complex number
	 * @return true if this complex number is a (of an infinite number)
	 * logarithm to the provided base of the other complex number, otherwise false
	 */
	public boolean isLog(Hypercomplex base, Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).isLog(base, other);
		}
		if (isBinary()) {
			return ((Binary)this).isLog(base, other);
		}
		if (isDual()) {
			return ((Dual)this).isLog(base, other);
		}
		return false;
	}

	/**
	 * Returns true if this complex number is one (of infinite) complex numbers that is x to the power of w<br>
	 * <b>Note</b> that if the exponent is real there are infinite solutions,
	 * using the function isPow(Complex x, int a, int n) however checks for a finite number of solutions.
	 * @param x the complex base
	 * @param w the complex exponent
	 * @return true if this complex number is one (of infinite) complex numbers that is x to the power of w
	 */
	public boolean isPow(Hypercomplex x, Hypercomplex w) {
		if (isComplex()) {
			return ((Complex)this).isPow(x, w);
		}
		if (isBinary()) {
			return ((Binary)this).isPow(x, w);
		}
		if (isDual()) {
			return ((Dual)this).isPow(x, w);
		}
		return false;
	}

	/**
	 * Returns true if this is x to the power of (a / n).
	 * @param x the complex base
	 * @param a the numerator of the exponent
	 * @param n the denominator of the exponent
	 * @return true if this is x to the power of (a / n) otherwise false
	 */
	public boolean isPow(Hypercomplex x, int a, int n) {
		if (isComplex()) {
			return ((Complex)this).isPow(x, a, n);
		}
		if (isBinary()) {
			return ((Binary)this).isPow(x, a, n);
		}
		if (isDual()) {
			return ((Dual)this).isPow(x, a, n);
		}
		return false;
	}

	/**
	 * Returns true if this is the n-th root of x.
	 * @param x the complex base
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return true if this is the n-th root of x otherwise false
	 */
	public boolean isRoot(Hypercomplex x, int n) {
		if (isComplex()) {
			return ((Complex)this).isRoot(x, n);
		}
		if (isBinary()) {
			return ((Binary)this).isRoot(x, n);
		}
		if (isDual()) {
			return ((Dual)this).isRoot(x, n);
		}
		return false;
	}

	/**
	 * Returns true if this complex number is real
	 * @return true if this complex number is real
	 */
	public boolean isReal() {
		if (isComplex()) {
			return ((Complex)this).isReal();
		}
		if (isBinary()) {
			return Complex.complex(this).isReal();
		}
		if (isDual()) {
			return Complex.complex(this).isReal();
		}
		return false;
	}

	/**
	 * Returns true if this complex number is integer
	 * @return true if this complex number is integer
	 */
	public boolean isRealInteger() {
		if (isComplex()) {
			return ((Complex)this).isRealInteger();
		}
		if (isBinary()) {
			return Complex.complex(this).isRealInteger();
		}
		if (isDual()) {
			return Complex.complex(this).isRealInteger();
		}
		return false;
	}
	
	// ------------------------- NON-STATIC INTERFACE (VECTOR-SPECIFIC OPERATIONS) -------------------------

	/**
	 * Returns a copy of the vector that is that is turned by the provided angle.
	 * @param rad the (radian) angle
	 * @return a copy of the vector that is that is turned by the provided angle
	 */
	public Hypercomplex turnedBy(double rad) {
		if (isComplex()) {
			return ((Complex)this).turnedBy(rad);
		}
		if (isBinary()) {
			return ((Binary)this).turnedBy(rad);
		}
		if (isDual()) {
			return ((Dual)this).turnedBy(rad);
		}
		return null;
	}

	/**
	 * Returns the dot product of this vector with the provided vector.
	 * @param other the other vector
	 * @return the dot product of this vector with the provided vector
	 */
	public double dot(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).dot(other);
		}
		if (isBinary()) {
			return Complex.complex(this).dot(other);
		}
		if (isDual()) {
			return Complex.complex(this).dot(other);
		}
		return Double.NaN;
	}

	/**
	 * Returns the dot product of this vector with itself.
	 * @return the dot product of this vector with itself
	 */
	public double dot() {
		if (isComplex()) {
			return ((Complex)this).dot();
		}
		if (isBinary()) {
			return Complex.complex(this).dot();
		}
		if (isDual()) {
			return Complex.complex(this).dot();
		}
		return Double.NaN;
	}

	/**
	 * Returns the determinant of this complex number.
	 * @return the determinant of this complex number
	 */
	public double det() {
		if (isComplex()) {
			return ((Complex)this).det();
		}
		if (isBinary()) {
			return ((Binary)this).det();
		}
		if (isDual()) {
			return ((Dual)this).det();
		}
		return Double.NaN;
	}
	
	/**
	 * Returns a copy of this vector with the length of 1.
	 * @return a copy of this vector with the length of 1
	 */
	public Hypercomplex r0() {
		if (isComplex()) {
			return ((Complex)this).r0();
		}
		if (isBinary()) {
			return ((Binary)this).r0();
		}
		if (isDual()) {
			return ((Dual)this).r0();
		}
		return null;
	}
	
	/**
	 * Returns a copy of this vector with the length of the old length to the power of n.
	 * @param n the power
	 * @return a copy of this vector with the length of the old length to the power of n
	 */
	public Hypercomplex r(double n) {
		if (isComplex()) {
			return ((Complex)this).r(n);
		}
		if (isBinary()) {
			return ((Binary)this).r(n);
		}
		if (isDual()) {
			return ((Dual)this).r(n);
		}
		return null;
	}

	/**
	 * Returns the (radian) angle from this vector respective to the provided vector.
	 * @param other the other vector
	 * @return the (radian) angle from this vector respective to the provided vector
	 */
	public double angleTo(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).angleTo(other);
		}
		if (isBinary()) {
			return Complex.complex(this).angleTo(other);
		}
		if (isDual()) {
			return Complex.complex(this).angleTo(other);
		}
		return Double.NaN;
	}

	/**
	 * Returns true if this vector does in any way (less than 90° difference) points toward the provided vector otherwise it returns false.
	 * @param other the other vector
	 * @return true if this vector does in any way (less than 90° difference) points toward the provided vector otherwise false
	 */
	public boolean pointsTowards(Hypercomplex other) {
		if (isComplex()) {
			return ((Complex)this).pointsTowards(other);
		}
		if (isBinary()) {
			return Complex.complex(this).pointsTowards(other);
		}
		if (isDual()) {
			return Complex.complex(this).pointsTowards(other);
		}
		return false;
	}

	/**
	 * Returns the vector with the contribution of this vector in direction of the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector in direction of the provided vector
	 */
	public Hypercomplex partInDirection(Hypercomplex r) {
		if (isComplex()) {
			return ((Complex)this).partInDirection(r);
		}
		if (isBinary()) {
			return ((Binary)this).partInDirection(r);
		}
		if (isDual()) {
			return ((Dual)this).partInDirection(r);
		}
		return null;
	}

	/**
	 * Returns the vector with the contribution of this vector orthogonally to the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector orthogonally to the provided vector
	 */
	public Hypercomplex partOrthogonallyTo(Hypercomplex r) {
		if (isComplex()) {
			return ((Complex)this).partOrthogonallyTo(r);
		}
		if (isBinary()) {
			return ((Binary)this).partOrthogonallyTo(r);
		}
		if (isDual()) {
			return ((Dual)this).partOrthogonallyTo(r);
		}
		return null;
	}

	/**
	 * Hilbert-Gram's Orthogonalization.<br>
	 * Divides a vector into the part in a direction and the rest.
	 * @param r direction to split in
	 * @return an arraylist with two vectors.<br>
	 * the first one holds the part in direction of r,<br>
	 * the other one holds the rest of the original vector.
	 */
	public ArrayList<? extends Hypercomplex> hilbert(Hypercomplex r) {
		if (isComplex()) {
			return ((Complex)this).hilbert(r);
		}
		if (isBinary()) {
			return ((Binary)this).hilbert(r);
		}
		if (isDual()) {
			return ((Dual)this).hilbert(r);
		}
		return null;
	}

	/**
	 * Returns this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r))
	 */
	public Hypercomplex mirroredRadialTo(Hypercomplex r) {
		if (isComplex()) {
			return ((Complex)this).mirroredRadialTo(r);
		}
		if (isBinary()) {
			return ((Binary)this).mirroredRadialTo(r);
		}
		if (isDual()) {
			return ((Dual)this).mirroredRadialTo(r);
		}
		return null;
	}

	/**
	 * Returns this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r))
	 */
	public Hypercomplex mirroredOrthogonalTo(Hypercomplex r) {
		if (isComplex()) {
			return ((Complex)this).mirroredOrthogonalTo(r);
		}
		if (isBinary()) {
			return ((Binary)this).mirroredOrthogonalTo(r);
		}
		if (isDual()) {
			return ((Dual)this).mirroredOrthogonalTo(r);
		}
		return null;
	}

	// ------------------------- MERE SETTER FUNCTIONS (USING OTHER METHODS) -------------------------

	/**
	 * Adds the given vector to this vector (changing its value).
	 * @param other the other vector
	 */
	public void add(Hypercomplex other) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).plus(other));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).plus(other));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).plus(other));
		}
	}

	/**
	 * Substracts the given vector from this vector (changing its value).
	 * @param other the other vector
	 */
	public void substract(Hypercomplex other) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).minus(other));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).minus(other));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).minus(other));
		}
	}

	/**
	 * Multiplies this vector with the given factor (changing its value).
	 * @param factor the factor
	 */
	public void multiply(double factor) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).times(factor));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).times(factor));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).times(factor));
		}
	}

	/**
	 * Divides the given vector to this vector (changing its value).
	 * @param divisor the divisor
	 */
	public void divide(double divisor) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).by(divisor));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).by(divisor));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).by(divisor));
		}
	}

	/**
	 * Sets this complex number to the (complex) product of this complex number and the given complex factor.
	 * @param factor the (complex) factor
	 */
	public void multiply(Hypercomplex factor) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).times(factor));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).times(factor));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).times(factor));
		}
	}

	/**
	 * Sets this complex number to the (complex) quotient of this complex number and the given complex divisor.
	 * @param divisor the (complex) divisor
	 */
	public void divide(Hypercomplex divisor) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).by(divisor));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).by(divisor));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).by(divisor));
		}
	}

	/**
	 * Sets this complex number to the complex number that is the (complex) inverse of this complex number.
	 */
	public void setInverse() {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).inverse());
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).inverse());
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).inverse());
		}
	}

	/**
	 * Sets this complex number to the complex number that is the complex conjugate of this complex number.
	 */
	public void setConjugate() {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).conjugate());
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).conjugate());
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).conjugate());
		}
	}

	/**
	 * Sets this complex number to this complex number to the power p.
	 */
	public void setPow(double p) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).pow(p));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).pow(p));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).pow(p));
		}
	}

	/**
	 * Sets this complex number to e to the power of this complex number.
	 */
	public void setExp() {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).exp());
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).exp());
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).exp());
		}
	}

	/**
	 * Sets this complex number to its (principal) natural logarithm.
	 */
	public void setLn() {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).ln());
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).ln());
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).ln());
		}
	}

	/**
	 * Sets this complex number to its (principal) logarithm to the base of b.
	 * @param b the complex base
	 */
	public void setLog(Hypercomplex b) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).log(b));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).log(b));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).log(b));
		}
	}
	
	/**
	 * Sets this complex number to itself to the power of the other provided complex exponent.
	 * @param w the complex exponent
	 */
	public void setPow(Hypercomplex w) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).pow(w));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).pow(w));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).pow(w));
		}
	}

	/**
	 * Turns the vector by the provided angle.
	 * @param rad the (radian) angle
	 */
	public void turn(double rad) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).turnedBy(rad));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).turnedBy(rad));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).turnedBy(rad));
		}
	}

	/**
	 * Sets this vector to its version that is mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r)).
	 * @param r the other position
	 */
	public void mirrorRadialTo(Hypercomplex r) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).mirroredRadialTo(r));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).mirroredRadialTo(r));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).mirroredRadialTo(r));
		}
	}

	/**
	 * Sets this vector to its version that is mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r)).
	 * @param r the other position
	 */
	public void mirrorOrthogonalTo(Hypercomplex r) {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).mirroredOrthogonalTo(r));
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).mirroredOrthogonalTo(r));
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).mirroredOrthogonalTo(r));
		}
	}
	
	/**
	 * Normalizes this vector (changing its length to 1).
	 */
	public void normalize() {
		if (isComplex()) {
			((Complex)this).set(((Complex)this).r0());
		}
		if (isBinary()) {
			((Binary)this).set(((Binary)this).r0());
		}
		if (isDual()) {
			((Dual)this).set(((Dual)this).r0());
		}
	}

	// ------------------------- MERE GETTER FUNCTIONS -------------------------


	/**
	 * Returns the cartesian version of this vector
	 * @return the cartesian version of this vector
	 */
	public Cartesian2D getCartesian() {
		if (cartVec == null) {
			cartVec = polVec.getCartesian();
		}
		return cartVec;
	}

	/**
	 * Returns the polynominal version of this vector
	 * @return the polynominal version of this vector
	 */
	public Polynominal2D getPolynominal() {
		if (polVec == null) {
			polVec = cartVec.getPolynominal();
		}
		return polVec;
	}

	/**
	 * Returns the (cartesian) x ordinate of this vector.
	 * @return the (cartesian) x ordinate of this vector
	 */
	public double x() { return getCartesian().getX(); }

	/**
	 * Returns the (cartesian) y ordinate of this vector.
	 * @return the (cartesian) y ordinate of this vector
	 */
	public double y() { return getCartesian().getY(); }

	/**
	 * Returns the (polynominal) length of this vector.
	 * @return the (polynominal) length of this vector
	 */
	public double length() { return getPolynominal().getLength(); }

	/**
	 * Returns the (polynominal) length of this vector.
	 * @return the (polynominal) length of this vector
	 */
	public double r() { return length(); }

	/**
	 * Returns the (polynominal) length of this vector.
	 * @return the (polynominal) length of this vector
	 */
	public double abs() { return length(); }

	/**
	 * Returns the (polynominal) angle/direction of this vector.
	 * @return the (polynominal) angle/direction of this vector
	 */
	public double direction() { return getPolynominal().getDirection(); }

	/**
	 * Returns the (polynominal) angle/direction of this vector.
	 * @return the (polynominal) angle/direction of this vector
	 */
	public double angle() { return getPolynominal().getDirection(); }

	/**
	 * Returns the (polynominal) angle/direction of this vector.
	 * @return the (polynominal) angle/direction of this vector
	 */
	public double phi() { return direction(); }

	/**
	 * Returns the real part of this complex number.
	 * @return the real part of this complex number
	 */
	public double real() { return x(); }

	/**
	 * Returns the real part of this complex number.
	 * @return the real part of this complex number
	 */
	public double re() { return x(); }

	/**
	 * Returns the imaginary part of this complex number.
	 * @return the imaginary part of this complex number
	 */
	public double imaginary() { return y(); }

	/**
	 * Returns the imaginary part of this complex number.
	 * @return the imaginary part of this complex number
	 */
	public double im() { return y(); }
	
	/**
	 * Returns the angle phi for the Z = r * e^(phi * i) equation (with positive r).
	 * @return the angle phi for the Z = r * e^(phi * i) equation (with positive r)
	 */
	public double eulerAngle() {
		if (isComplex()) {
			return ((Complex)this).eulerAngle();
		}
		if (isBinary()) {
			return ((Binary)this).eulerAngle();
		}
		if (isDual()) {
			return ((Dual)this).eulerAngle();
		}
		return Double.NaN;
	}
	
	/**
	 * Returns the length r for the Z = r * e^(phi * i) equation (with positive r).
	 * @return the length r for the Z = r * e^(phi * i) equation (with positive r)
	 */
	public double eulerLength() {
		if (isComplex()) {
			return ((Complex)this).eulerLength();
		}
		if (isBinary()) {
			return ((Binary)this).eulerLength();
		}
		if (isDual()) {
			return ((Dual)this).eulerLength();
		}
		return Double.NaN;
	}
	
	public Color color() {
		// determine color
		double phi = phi();
		double r = (Math.cos(phi) + 1) / 2;
		double g = (Math.cos(phi + 2 * Math.PI / 3) + 1) / 2;
		double b = (Math.cos(phi - 2 * Math.PI / 3) + 1) / 2;
		// determine brightness
		double lengthFactor = 1e1;

		double intensity = 1d / Math.log(Math.abs(Complex.complex(this).eulerLength()) * lengthFactor + Math.E);
		double leave = 0.2;
		intensity = leave * 255 + (1 - leave) * intensity * 255;
		double range = Math.min(255 - intensity, intensity - leave * 255);
		// make infinity not black for all directions
		// draw point
		return new Color((int)Math.round(intensity + r * range), (int)Math.round(intensity + g * range), (int)Math.round(intensity + b * range));
	}
	
	// ------------------------- TRIGONOMETRIC FUNCTIONS -------------------------
	
	/**
	 * inverse hyperbolic sine
	 * @param x argument
	 * @return inverse hyperbolic sine
	 */
	public static double asinh(double x) {
		return Math.log(x + Math.sqrt(x * x + 1));
	}
	
	/**
	 * inverse hyperbolic cosine
	 * @param x argument
	 * @return inverse hyperbolic cosine
	 */
	public static double acosh(double x) {
		return Math.log(x + Math.sqrt(x * x - 1));
	}
	
	/**
	 * sine
	 * @return sine
	 */
	public Hypercomplex sin() {
		if (isComplex()) {
			return ((Complex)this).sin();
		}
		if (isBinary()) {
			return ((Binary)this).sin();
		}
		if (isDual()) {
			return ((Dual)this).sin();
		}
		return null;
	}
	
	/**
	 * cosine
	 * @return cosine
	 */
	public Hypercomplex cos() {
		if (isComplex()) {
			return ((Complex)this).cos();
		}
		if (isBinary()) {
			return ((Binary)this).cos();
		}
		if (isDual()) {
			return ((Dual)this).cos();
		}
		return null;
	}
	
	/**
	 * tangent
	 * @return tangent
	 */
	public Hypercomplex tan() {
		if (isComplex()) {
			return ((Complex)this).sin().by(((Complex)this).cos());
		}
		if (isBinary()) {
			return ((Binary)this).sin().by(((Binary)this).cos());
		}
		if (isDual()) {
			return ((Dual)this).sin().by(((Dual)this).cos());
		}
		return null;
	}

	/**
	 * cotangent
	 * @return cotangent
	 */
	public Hypercomplex cot() {
		if (isComplex()) {
			return ((Complex)this).cos().by(((Complex)this).sin());
		}
		if (isBinary()) {
			return ((Binary)this).cos().by(((Binary)this).sin());
		}
		if (isDual()) {
			return ((Dual)this).cos().by(((Dual)this).sin());
		}
		return null;
	}
	
	/**
	 * secant
	 * @return secant
	 */
	public Hypercomplex sec() {
		if (isComplex()) {
			return ((Complex)this).cos().inverse();
		}
		if (isBinary()) {
			return ((Binary)this).cos().inverse();
		}
		if (isDual()) {
			return ((Dual)this).cos().inverse();
		}
		return null;
	}

	/**
	 * cosecant
	 * @return cosecant
	 */
	public Hypercomplex csc() {
		if (isComplex()) {
			return ((Complex)this).sin().inverse();
		}
		if (isBinary()) {
			return ((Binary)this).sin().inverse();
		}
		if (isDual()) {
			return ((Dual)this).sin().inverse();
		}
		return null;
	}

	/**
	 * inverse sine
	 * @return inverse sine
	 */
	public Hypercomplex asin() {
		if (isComplex()) {
			return ((Complex)this).asin();
		}
		if (isBinary()) {
			return ((Binary)this).asin();
		}
		if (isDual()) {
			return ((Dual)this).asin();
		}
		return null;
	}

	/**
	 * inverse cosine
	 * @return inverse cosine
	 */
	public Hypercomplex acos() {
		if (isComplex()) {
			return ((Complex)this).acos();
		}
		if (isBinary()) {
			return ((Binary)this).acos();
		}
		if (isDual()) {
			return ((Dual)this).acos();
		}
		return null;
	}

	/**
	 * inverse tangent
	 * @return inverse tangent
	 */
	public Hypercomplex atan() {
		if (isComplex()) {
			return ((Complex)this).atan();
		}
		if (isBinary()) {
			return ((Binary)this).atan();
		}
		if (isDual()) {
			return ((Dual)this).atan();
		}
		return null;
	}

	/**
	 * inverse cotangent
	 * @return inverse cotangent
	 */
	public Hypercomplex acot() {
		if (isComplex()) {
			return ((Complex)this).acot();
		}
		if (isBinary()) {
			return ((Binary)this).acot();
		}
		if (isDual()) {
			return ((Dual)this).acot();
		}
		return null;
	}

	/**
	 * inverse secant
	 * @return inverse secant
	 */
	public Hypercomplex asec() {
		if (isComplex()) {
			return ((Complex)this).asec();
		}
		if (isBinary()) {
			return ((Binary)this).asec();
		}
		if (isDual()) {
			return ((Dual)this).asec();
		}
		return null;
	}

	/**
	 * inverse cosecant
	 * @return inverse cosecant
	 */
	public Hypercomplex acsc() {
		if (isComplex()) {
			return ((Complex)this).acsc();
		}
		if (isBinary()) {
			return ((Binary)this).acsc();
		}
		if (isDual()) {
			return ((Dual)this).acsc();
		}
		return null;
	}

	/**
	 * hyperbolic sine
	 * @return hyperbolic sine
	 */
	public Hypercomplex sinh() {
		if (isComplex()) {
			return ((Complex)this).sinh();
		}
		if (isBinary()) {
			return ((Binary)this).sinh();
		}
		if (isDual()) {
			return ((Dual)this).sinh();
		}
		return null;
	}

	/**
	 * hyperbolic cosine
	 * @return hyperbolic cosine
	 */
	public Hypercomplex cosh() {
		if (isComplex()) {
			return ((Complex)this).cosh();
		}
		if (isBinary()) {
			return ((Binary)this).cosh();
		}
		if (isDual()) {
			return ((Dual)this).cosh();
		}
		return null;
	}

	/**
	 * hyperbolic tangent
	 * @return hyperbolic tan
	 */
	public Hypercomplex tanh() {
		if (isComplex()) {
			return ((Complex)this).sinh().by(((Complex)this).cosh());
		}
		if (isBinary()) {
			return ((Binary)this).sinh().by(((Binary)this).cosh());
		}
		if (isDual()) {
			return ((Dual)this).sinh().by(((Dual)this).cosh());
		}
		return null;
	}

	/**
	 * hyperbolic cotangent
	 * @return hyperbolic cotan
	 */
	public Hypercomplex coth() {
		if (isComplex()) {
			return ((Complex)this).cosh().by(((Complex)this).sinh());
		}
		if (isBinary()) {
			return ((Binary)this).cosh().by(((Binary)this).sinh());
		}
		if (isDual()) {
			return ((Dual)this).cosh().by(((Dual)this).sinh());
		}
		return null;
	}

	/**
	 * hyperbolic secant
	 * @return hyperbolic secant
	 */
	public Hypercomplex sech() {
		if (isComplex()) {
			return ((Complex)this).cosh().inverse();
		}
		if (isBinary()) {
			return ((Binary)this).cosh().inverse();
		}
		if (isDual()) {
			return ((Dual)this).cosh().inverse();
		}
		return null;
	}

	/**
	 * hyperbolic cosecant
	 * @return hyperbolic cosecant
	 */
	public Hypercomplex csch() {
		if (isComplex()) {
			return ((Complex)this).sinh().inverse();
		}
		if (isBinary()) {
			return ((Binary)this).sinh().inverse();
		}
		if (isDual()) {
			return ((Dual)this).sinh().inverse();
		}
		return null;
	}

	/**
	 * inverse hyperbolic sine
	 * @return inverse hyperbolic sine
	 */
	public Hypercomplex asinh() {
		if (isComplex()) {
			return ((Complex)this).asinh();
		}
		if (isBinary()) {
			return ((Binary)this).asinh();
		}
		if (isDual()) {
			return ((Dual)this).asinh();
		}
		return null;
	}

	/**
	 * inverse hyperbolic cosine
	 * @return inverse hyperbolic cosine
	 */
	public Hypercomplex acosh() {
		if (isComplex()) {
			return ((Complex)this).acosh();
		}
		if (isBinary()) {
			return ((Binary)this).acosh();
		}
		if (isDual()) {
			return ((Dual)this).acosh();
		}
		return null;
	}

	/**
	 * inverse hyperbolic tangent
	 * @return inverse hyperbolic tangent
	 */
	public Hypercomplex atanh() {
		if (isComplex()) {
			return ((Complex)this).atanh();
		}
		if (isBinary()) {
			return ((Binary)this).atanh();
		}
		if (isDual()) {
			return ((Dual)this).atanh();
		}
		return null;
	}

	/**
	 * inverse hyperbolic cotangent
	 * @return inverse hyperbolic cotangent
	 */
	public Hypercomplex acoth() {
		if (isComplex()) {
			return ((Complex)this).inverse().atanh();
		}
		if (isBinary()) {
			return ((Binary)this).inverse().atanh();
		}
		if (isDual()) {
			return ((Dual)this).inverse().atanh();
		}
		return null;
	}

	/**
	 * inverse hyperbolic secant
	 * @return inverse hyperbolic secant
	 */
	public Hypercomplex asech() {
		if (isComplex()) {
			return ((Complex)this).inverse().acosh();
		}
		if (isBinary()) {
			return ((Binary)this).inverse().acosh();
		}
		if (isDual()) {
			return ((Dual)this).inverse().acosh();
		}
		return null;
	}

	/**
	 * inverse hyperbolic cosecant
	 * @return inverse hyperbolic cosecant
	 */
	public Hypercomplex acsch() {
		if (isComplex()) {
			return ((Complex)this).inverse().asinh();
		}
		if (isBinary()) {
			return ((Binary)this).inverse().asinh();
		}
		if (isDual()) {
			return ((Dual)this).inverse().asinh();
		}
		return null;
	}

	// ------------------------- OVERRIDING PREVIOUSLY EXISTING FUNCTIONS -------------------------
	
	/**
	 * Returns true if the provided complex numbers are (to the greatest extend) equals, otherwise it returns false.
	 * @param other the complex number to compare with
	 * @return true if the provided complex numbers are (to the greatest extend) equals, otherwise false
	 */
	@Override
	public boolean equals(Object other) {
		return equals(other, 1);
	}
	
	/**
	 * Returns true if the provided complex numbers are (to the greatest extend) equals, otherwise it returns false.
	 * @param other the complex number to compare with
	 * @return true if the provided complex numbers are (to the greatest extend) equals, otherwise false
	 */
	public boolean equals(Object other, double inaccuracy) {
		if (!(other instanceof Number)) {
			return false;
		}
		if (other instanceof Hypercomplex) {
			if (!((Hypercomplex)other).isReal() || !this.isReal()) {
				if ((Complex.class.isInstance(this) && !Complex.class.isInstance(other))
						|| (Complex.class.isInstance(other) && !Complex.class.isInstance(this))) {
					return false;
				}
				if ((Binary.class.isInstance(this) && !Binary.class.isInstance(other))
						|| (Binary.class.isInstance(other) && !Binary.class.isInstance(this))) {
					return false;
				}
				if ((Dual.class.isInstance(this) && !Dual.class.isInstance(other))
						|| (Dual.class.isInstance(other) && !Dual.class.isInstance(this))) {
					return false;
				}
			}
			return Tests.compareValue(re(), ((Hypercomplex)other).re(), inaccuracy)
				&& Tests.compareValue(im(), ((Hypercomplex)other).im(), inaccuracy);
		}
		return isReal() && Tests.compareValue(re(), ((Number)other).doubleValue(), inaccuracy);
	}

	/**
	 * Returns the hashCode of the String representing this complex number.
	 * @return the hashCode of the String representing this complex number
	 */
	@Override
	public int hashCode() {
		return toString().hashCode();
	}

	/**
	 * Returns a String representing this complex number.
	 * @return a String representing this complex number
	 */
	@Override
	public String toString() {
		return getCartesian().toString();
	}

	/**
	 * Returns the real part of this complex number casted to double.
	 * @return the real part of this complex number casted to double
	 */
	@Override
	public double doubleValue() {
		return re();
	}

	/**
	 * Returns the real part of this complex number casted to float.
	 * @return the real part of this complex number casted to float
	 */
	@Override
	public float floatValue() {
		return (float)re();
	}

	/**
	 * Returns the real part of this complex number casted to int (rounded).
	 * @return the real part of this complex number casted to int (rounded)
	 */
	@Override
	public int intValue() {
		return (int)(re() + 0.5);
	}


	/**
	 * Returns the real part of this complex number casted to int (rounded).
	 * @return the real part of this complex number casted to int (rounded)
	 */
	public int round() {
		return intValue();
	}

	/**
	 * Returns the real part of this complex number casted to int (rounded).
	 * @return the real part of this complex number casted to int (rounded)
	 */
	public int ceil() {
		return (int)((int)re() == re() ? re() : re() + 1);
	}

	/**
	 * Returns the real part of this complex number casted to int (rounded).
	 * @return the real part of this complex number casted to int (rounded)
	 */
	public int floor() {
		return (int)re();
	}

	/**
	 * Returns the real part of this complex number casted to long.
	 * @return the real part of this complex number casted to long
	 */
	public long longValue() {
		return (long)(re() + 0.5);
	}

	/**
	 * Compares the real part of this complex number to the real part of another one.
	 * @param other the complex number to compare with
	 * @return -1 if this is less, 0 if this is equal or 1 if this is greater 
	 */
	@Override
	public int compareTo(Number other) {
		if (Tests.compareValue(doubleValue(), other.doubleValue())) {
			return 0;
		} else {
			if (doubleValue() < other.doubleValue()) {
				return -1;
			} else {
				return 1;
			}
		}
	}

	/**
	 * Returns a copy of this complex number.
	 * @return a copy of this complex number
	 */
	@Override
	public Hypercomplex clone() {
		return this.times(1);
	}

	public boolean isComplex() {
		return complex;
	}

	public void setComplex(boolean complex) {
		this.complex = complex;
	}

	public boolean isBinary() {
		return binary;
	}

	public void setBinary(boolean binary) {
		this.binary = binary;
	}

	public boolean isDual() {
		return dual;
	}

	public void setDual(boolean dual) {
		this.dual = dual;
	}
	
}
