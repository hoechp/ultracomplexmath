package util.hypercomplex;


import java.awt.Color;
import java.util.ArrayList;


import util.tests.Tests;

/**
 * A complex number.<p>
 * 
 * (May z, z1, z2 be complex numbers)<p>
 * Constructor use:<br>
 * <b>examples:</b><br>
 * z = new Complex(); <- creates a complex number with RE = IM = 0<br>
 * z = new Complex(1d); <- creates a complex number with RE = 1, IM = 0<br>
 * z = new Complex(1d, 2d); <- creates a (cartesian) complex number with RE = 1, IM = 2<br>
 * z = new Complex("c", 1d, 2d); <- creates a (cartesian) complex number with <b>RE</b> = 1, <b>IM</b> = 2<br>
 * z = new Complex("p", 1d, 2d); <- creates a (polynominal) complex number with <b>R</b> = 1, <b>PHI</b> = 2<br>
 * ...<p>
 * 
 * Getting the most important values:<br>
 * <b>examples:</b><br>
 * double value = z.re() <- real part<br>
 * double value = z.im() <- imaginary part<br>
 * double value = z.r() <- length<br>
 * double value = z.phi() <- angle<br>
 * ...<p>
 * 
 * The main complex operations:<br>
 * <b>examples:</b><br>
 * z = z1.plus(z2); <- returns z1 + z2<br>
 * z = z1.minus(z2); <- returns z1 - z2<br>
 * z = z1.times(z2); <- returns z1 * z2<br>
 * z = z1.by(z2); <- returns z1 / z2<br>
 * z = z1.exp(); <- returns e^z1 (principal value)<br>
 * z = z1.ln(); <- returns ln(z1) (principal value)<br>
 * z = z1.pow(z2); <- returns z1^z2 (principal value)<br>
 * z = z1.log(z2); <- returns log_z2(z1) (principal value)<br>
 * z = z1.conjugate(); <- returns the complex conjugate of z1<br>
 * z = z1.inverse(); <- returns the inverse of z1<br>
 * ...<br>
 * Nearly all of those functions have analog versions that directly set that value to the first one.
 * And some functions have static analog versions as well (pow, exp, ln, log, sqrt).<p>
 * 
 * Other more vector specific functions:<br>
 * <b>examples:</b><br>
 * z = z1.turnedBy(Math.PI / 2) <- returns z1 turned by 90°<br>
 * boolean check = z1.pointsTowards(z2) <- returns if z1 has any part in z2's direction<br>
 * double dot = z1.dot(z2) <- returns the dot-product of z1 and z2 (interpreting them as vectors)<br>
 * z = z1.partInDirection(z2) <- returns z1's part in z2's direction (analog: z1.partOrthogonallyTo(z2))<br>
 * ...<p>
 * 
 * The class also provides some basic constants like the complex numbers ZERO, ONE, and I.<p>
 * 
 * There are also some sophisticated methods of determining if a complex number is z1.pow(z2) or z1.log(z2).<br>
 * It is impossible to determine exactly what solutions lie in z1.pow(z2) if z2 is real
 * (not zero and without imaginary part). Thats due to z2.re() being a real number with limited precision
 * that therefore always could take any value between -PI and PI if you multiply it with higher
 * and higher integers and keep normalizing it into the strip between -PI and PI
 * what is essentially what must be done in the necessary calculations.<br>
 * So for the case that the real part of the exponent is really a <b>rational number</b> a method is provided
 * that is then able to determine if a complex number z is z1.pow(numerator, denominator).<br>
 * <b>examples:</b><br>
 * boolean check = I.isPow(ONE, 1, 4); <- returns true since I is a solution of ONE^(1/4)<br>
 * boolean check = z.isPow(z1, z2); <- returns true if z is one solution of z1^z2<br>
 * boolean check = z.isLog(z1, z2); <- returns true if z is one solution of log_z1(z2)<br>
 * ...<p>
 * Some methods return only the principal value of unlimited solutions.<br>
 * But some methods return an ArrayList&ltComplex&gt list, that hold all the solutions.
 * That can only be the case if the expression is of the type Complex
 * to the power of a rational number (sqrt(), roots(n), pow(a, n)).<br>
 * @see Number
 * @see Comparable
 * @see Cloneable
 * @author Philipp Kolodziej
 */
public class Complex extends Hypercomplex {

	// ------------------------- PRIVATE FIELD DATA -------------------------

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
	public final static int DISPLAYED_CIPHER_COUNT = 4;
	
	/**
	 * complex number equaling the real number ONE
	 */
	public final static Complex ONE = new Complex(1);
	
	/**
	 * complex number equaling the real number ZERO
	 */
	public final static Complex ZERO = new Complex();
	
	/**
	 * complex number equaling the imaginary number I
	 */
	public final static Complex I = new Complex(0, 1);
	
	/**
	 * complex number equaling the real number E
	 */
	public final static Complex E = new Complex(Math.E);

	// ------------------------- STATIC INTERFACE (FUNCTIONS) -------------------------
	
	/**
	 * Complex exponential function. Returns e^x with x being the complex exponent.
	 * @param x the complex exponent
	 * @return e^x with x being the complex exponent
	 */
	public static Complex exp(Hypercomplex x) {
		return E.pow(x);
	}

	/**
	 * Complex natural logarithm (principal value). Returns ln(x) with x being the complex argument.
	 * @param x the complex argument
	 * @return ln(x) with x being the complex argument
	 */
	public static Complex ln(Hypercomplex x) {
		return ((Complex)x).ln();
	}

	/**
	 * Complex logarithm (principal value) of x to the base of b.
	 * Returns log_b(x) with x being the complex argument, b being the complex base.
	 * @param b the complex base
	 * @param x the complex argument
	 * @return log_b(x) with x being the complex argument, b being the complex base
	 */
	public static Complex log(Hypercomplex b, Hypercomplex x) {
		return ((Complex)x).log(b);
	}

	/**
	 * Complex power. Returns x to the power of w.
	 * @param x the complex base
	 * @param w the complex exponent
	 * @return x to the power of w
	 */
	public static Complex pow(Hypercomplex x, Hypercomplex w) {
		return ((Complex)x).pow(w);
	}

	/**
	 * Complex power. Returns x to the power of w.
	 * @param x the complex base
	 * @param w the real exponent
	 * @return x to the power of w
	 */
	public static Complex pow(Hypercomplex x, double w) {
		return ((Complex)x).pow(w);
	}

	/**
	 * Principal value of the complex square root. Returns the principal square root of x.
	 * @param x the provided complex number
	 * @return the principal square root of x
	 */
	public static Complex sqrt(Hypercomplex x) {
		return ((Complex)x).pow(0.5);
	}

	// ------------------------- NON-STATIC INTERFACE (CONSTRUCTORS) -------------------------
	
	/**
	 * Constructor. Constructs a complex number containing the provided parsable data.
	 * @param parseData the String-representation of the number
	 */
	public Complex(String parseData) {
		setCartesian(parseHypercomplex(parseData).getCartesian());
	}
	
	/**
	 * constructor. constructs a vector containing the cartesian and polynominal values (0, 0).
	 */
	public Complex() {
		setPolynominal(0, 0);
		setComplex(true);
	}

	/**
	 * Constructor. Constructs a real complex number containing the provided real value.
	 * @param re the real part
	 */
	public Complex(double re) {
		setCartesian(re, 0);
		setComplex(true);
	}

	/**
	 * Constructor. Constructs a complex number containing the provided values.<br>
	 * <b>Note</b> the provided values will be treated as cartesian values.
	 * @param re the real part
	 * @param im the imaginary part
	 */
	public Complex(double re, double im) {
		setCartesian(re, im);
		setComplex(true);
	}

	/**
	 * Constructor. Constructs a complex number containing the provided values.<br>
	 * Use format == "p" or "P" and the values will be treated as polynominal.
	 * Use format == "c" or "C" and the values will be treated as cartesian.
	 * @param r the length or real part
	 * @param phi the angle or imaginary part
	 */
	public Complex(String format, double r, double phi) {
		if (format.equals("c") || format.equals("C")) {
			setCartesian(r, phi);
		} else if (format.equals("p") || format.equals("P")) {
			setPolynominal(r, phi);
		} else {
			setCartesian(Double.NaN, Double.NaN);
		}
		setComplex(true);
	}

	/**
	 * Converts Complex (potentially binary / dual) into Complex, just using the cartesian values.
	 * @param c the complex number to convert
	 * @return the complex number
	 */
	public static Complex complex(Hypercomplex c) {
		return new Complex(c.re(), c.im());
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

	/**
	 * Set the vector with polynominal parameters.
	 * @param pol the polynominal vector
	 */
	private void setPolynominal(Polynominal2D pol) {
		if (polVec == null) {
			polVec = new Polynominal2D();
		}
		polVec.set(0, pol.get(0));
		polVec.set(1, pol.get(1));
		polVec.checkDirectionAndAngle();
		cartVec = polVec.getCartesian();
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
	public Complex plus(Hypercomplex other) {
		Complex result = new Complex();
		result.setCartesian(getCartesian().plus(other.getCartesian()));
		result.setPolynominal(result.getCartesian().getPolynominal());
		return result;
	}

	/**
	 * Returns a vector that is the difference of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the difference of this vector and the given vector
	 */
	public Complex minus(Hypercomplex other) {
		Complex result = new Complex();
		result.setCartesian(getCartesian().minus(other.getCartesian()));
		result.setPolynominal(result.getCartesian().getPolynominal());
		return result;
	}

	/**
	 * Returns a vector that is the product of this vector and the given factor.
	 * @param factor the factor
	 * @return a vector that is the product of this vector and the given factor
	 */
	public Complex times(double factor) {
		Complex result = (new Complex());
		result.setPolynominal(getPolynominal().times(factor));
		result.setCartesian(result.getPolynominal().getCartesian());
		return result;
	}

	/**
	 * Returns a vector that is the quotient of this vector and the given divisor.
	 * @param divisor the divisor
	 * @return a vector that is the quotient of this vector and the given divisor
	 */
	public Complex by(double divisor) {
		Complex result = new Complex();
		result.setPolynominal(getPolynominal().by(divisor));
		result.setCartesian(result.getPolynominal().getCartesian());
		return result;
	}

	/**
	 * Returns a complex number that is the (complex) product of this complex number and the given complex factor.
	 * @param f the (complex) factor
	 * @return a complex number that is the (complex) product of this complex number and the given complex factor
	 */
	public Complex times(Hypercomplex f) {
		return new Complex(re() * f.re() - im() * f.im(), re() * f.im() + im() * f.re());
	}

	/**
	 * Returns a complex number that is the (complex) quotient of this complex number and the given complex divisor.
	 * @param d the (complex) divisor
	 * @return a complex number that is the (complex) quotient of this complex number and the given complex divisor
	 */
	public Complex by(Hypercomplex d) {
		return new Complex((re() * d.re() + im() * d.im()) / d.dot(), (im() * d.re() - re() * d.im()) / d.dot());
	}

	/**
	 * Returns a complex number that is the (complex) inverse of this complex number.
	 * @return a complex number that is the (complex) inverse of this complex number
	 */
	public Complex inverse() {
		return conjugate().by(det());
	}

	/**
	 * Returns a complex number that is the complex conjugate of this complex number.
	 * @return a complex number that is the complex conjugate of this complex number
	 */
	public Complex conjugate() {
		return new Complex(re(), -im());
	}

	/**
	 * Returns an ArrayList of the n complex numbers that are the n-th roots of this complex number.
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return an ArrayList of the n complex numbers that are the n-th roots of this complex number
	 */
	public ArrayList<? extends Hypercomplex> roots(int n) {
		return pow(1, n);
	}

	/**
	 * Returns an ArrayList of the n complex numbers that are this to the power of (a / n).
	 * @param a the numerator
	 * @param n the denominator
	 * @return an ArrayList of the n complex numbers that are this to the power of (a / n)
	 */
	public ArrayList<? extends Hypercomplex> pow(int a, int n) {
		if (n == 0) { // if the denominator is zero dividing through it is impossible
			return null;
		}
		if (n < 0) { // n must be positive, a can be negative
			a *= -1;
			n *= -1;
		}		
		int gcd, h0, h1 = Math.abs(a), h2 = n;
	    while (true) { // Euklid's GCD iterative
	        if (h2 == 0) {
	        	gcd = h1;
	        	break;
	        } else {
	        	h0 = h1 % h2;
	        	h1 = h2;
	        	h2 = h0;
	        }
	    }
	    a /= gcd;
	    n /= gcd;
	    // now since a and n are proper now the recognizable slightly modified complex roots formula comes to use
		ArrayList<Hypercomplex> result = new ArrayList<Hypercomplex>();
		for (int k = 0; k < n; ++k) {
			result.add(new Complex("p", Math.exp(Math.log(r()) * a / n), a * (2 * Math.PI * k + phi()) / n));
		}
		return result;
	}
	
	/**
	 * Returns a complex number that is this complex number to the power p.
	 * @param p the power
	 * @return a complex number that is this complex number to the power p
	 */
	public Complex pow(double p) {
		return new Complex("p", Math.pow(r(), p), phi() * p);
	}
	
	/**
	 * Returns the principal value of e to the power of this complex number.
	 * @return the principal value of e to the power of this complex number
	 */
	public Complex exp() {
		return new Complex(Math.cos(im()), Math.sin(im())).times(Math.exp(re()));
	}
	
	/**
	 * Returns the principal natural logarithm of this complex number.
	 * @return the principal natural logarithm of this complex number
	 */
	public Complex ln() {
		return new Complex(Math.log(r()), phi());
	}
	
	/**
	 * Complex logarithm (principal value) of this to the base of b.
	 * Returns log_b(this) with b being the complex base.
	 * @param b the complex base
	 * @return log_b(this) with b being the complex base
	 */
	public Complex log(Hypercomplex b) {
		Complex result = ln().by(b.ln());
		Complex principalHolder = new Complex("p", 0, result.im());
		result.setImaginary(principalHolder.phi());
		return result;
	}
	
	/**
	 * Returns the principal value of this complex number to the power of the other provided complex exponent.
	 * @param w the complex exponent
	 * @return the principal value of this complex number to the power of the other provided complex exponent
	 */
	public Complex pow(Hypercomplex w) { // z^w = exp(log(z) * w) = exp(a) * exp(b * i)
		return new Complex("p", Math.pow(r(), w.re()) * Math.exp(-w.im() * phi()), Math.log(Math.pow(r(), w.im()) * Math.exp(w.re() * phi())));
	}

	// ------------------------- NON-STATIC INTERFACE (TESTING COMPLEX NUMBERS) -------------------------

	/**
	 * Returns true if this complex number is one natural logarithm (of infinitely many) of the other complex number
	 * @param other the other complex number
	 * @return true if this complex number is one natural logarithm (of infinitely many) of the other complex number, otherwise false
	 */
	public boolean isLn(Hypercomplex other) {
		Complex principalHolder = new Complex("p", 0, im());
		Complex complexPrincipalValue = new Complex(re(), principalHolder.phi());
		if (complexPrincipalValue.equals(other.ln())) {
			return true;
		} else {
			return false;
		}
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
		Complex principalHolder = new Complex("p", 0, im());
		Complex complexPrincipalValue = new Complex(re(), principalHolder.phi());
		if (complexPrincipalValue.equals(other.log(base))) {
			return true;
		} else {
			return false;
		}
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
		/*
		 * approach:
		 * (r'; phi') of (r; phi; a; b)
		 * = (e^(a * log(r) - b * (2 * PI * n + phi));
		 * 	     b * log(r) + a * (2 * PI * n + phi))
		 * r == 0 -> RETURN false
		 * b == 0 -> a == 0 -> RETURN z.equals(ONE)
		 * 			 a != 0 -> RETURN (z.r() == r^a)
		 * b != 0 -> n = - (log(r' / r^a) + b * phi) / (2 * PI * b) // check if out int
		 * 			 phi' = b * log(r) + a/b * log(r' / r^a) // check if == z.phi
		 * 			 RETURN (checks went well)
		 */
		// to keep notation:
		double r = x.r();
		double phi = x.phi();
		double a = w.re();
		double b = w.im();
		double r2 = r();
		double phi2 = phi();
		// now the different cases:
		if (Math.abs(r) < Tests.DELTA) { // 0^q
			return false;
		}
		if (Math.abs(b) < Tests.DELTA) {
			if (Math.abs(a) < Tests.DELTA) { // q^0
				return equals(ONE);
			} else { // q^(p out R)
				return Math.abs(r2 - Math.pow(r, a)) < Tests.DELTA;
			}
		} else { // r != 0, b != 0 => |r2 out L| == infinity
			double n = -(Math.log(r2 / Math.pow(r, a)) + b * phi) / (2 * Math.PI * b);
			double nRest = Math.abs(n) % 1;
			if (nRest > 0.5) {
				nRest = 1 - nRest;
			}
			if (!Tests.compareValue(0, nRest)) {
				return false;
			}
			double phi3 = b * Math.log(r) + a * (2 * Math.PI * n + phi);
			Complex cPhi2 = new Complex("p", 1, phi2); // not the nicest way 
			Complex cPhi3 = new Complex("p", 1, phi3); // not the nicest way 
			double deg = Math.abs(cPhi2.angleTo(cPhi3)) % 2 * Math.PI;
			deg = Math.min(Math.abs(deg), Math.abs(2 * Math.PI - deg));
			return deg < Tests.DELTA;
		}
	}

	/**
	 * Returns true if this is x to the power of (a / n).
	 * @param x the complex base
	 * @param a the numerator of the exponent
	 * @param n the denominator of the exponent
	 * @return true if this is x to the power of (a / n) otherwise false
	 */
	public boolean isPow(Hypercomplex x, int a, int n) {
		return x.pow(a, n).contains(this);
	}

	/**
	 * Returns true if this is the n-th root of x.
	 * @param x the complex base
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return true if this is the n-th root of x otherwise false
	 */
	public boolean isRoot(Hypercomplex x, int n) {
		return x.roots(n).contains(this);
	}

	/**
	 * Returns true if this complex number is real
	 * @return true if this complex number is real
	 */
	public boolean isReal() {
		if ((Math.abs(im()) > Tests.DELTA
				|| ((Double)r()).isNaN()
				|| ((Double)r()).isInfinite())) {
			return false;
		} else {
			return true;
		}
	}

	/**
	 * Returns true if this complex number is integer
	 * @return true if this complex number is integer
	 */
	public boolean isRealInteger() {
		if (!isReal() ||
				(Math.abs(re()) % 1 > Tests.DELTA
				&& Math.abs(re()) % 1 < 1 - Tests.DELTA)) {
			return false;
		} else {
			return true;
		}
	}
	
	// ------------------------- NON-STATIC INTERFACE (VECTOR-SPECIFIC OPERATIONS) -------------------------

	/**
	 * Returns a copy of the vector that is that is turned by the provided angle.
	 * @param rad the (radian) angle
	 * @return a copy of the vector that is that is turned by the provided angle
	 */
	public Complex turnedBy(double rad) {
		Complex result = new Complex();
		result.setPolynominal(getPolynominal().turnedBy(rad));
		result.setCartesian(result.getPolynominal().getCartesian());
		return result;
	}

	/**
	 * Returns the dot product of this vector with the provided vector.
	 * @param other the other vector
	 * @return the dot product of this vector with the provided vector
	 */
	public double dot(Hypercomplex other) {
		return getCartesian().dot(other.getCartesian());
	}

	/**
	 * Returns the dot product of this vector with itself.
	 * @return the dot product of this vector with itself
	 */
	public double dot() {
		return dot(this);
	}

	/**
	 * Returns the determinant of this complex number.
	 * @return the determinant of this complex number
	 */
	public double det() {
		return dot();
	}
	
	/**
	 * Returns a copy of this vector with the length of 1.
	 * @return a copy of this vector with the length of 1
	 */
	public Complex r0() {
		return by(length());
	}
	
	/**
	 * Returns a copy of this vector with the length of the old length to the power of n.
	 * @param n the power
	 * @return a copy of this vector with the length of the old length to the power of n
	 */
	public Complex r(double n) {
		return times(Math.pow(r(), n) / length());
	}

	/**
	 * Returns the (radian) angle from this vector respective to the provided vector.
	 * @param other the other vector
	 * @return the (radian) angle from this vector respective to the provided vector
	 */
	public double angleTo(Hypercomplex other) {
		double result = phi() - other.phi();
		if (result <= -Math.PI) { // reensure -PI < phi <= PI
			result += 2 * Math.PI;
		}
		if (result > Math.PI) { // reensure -PI < phi <= PI
			result -= 2 * Math.PI;
		}
		return result;
	}

	/**
	 * Returns true if this vector does in any way (less than 90° difference) points toward the provided vector otherwise it returns false.
	 * @param other the other vector
	 * @return true if this vector does in any way (less than 90° difference) points toward the provided vector otherwise false
	 */
	public boolean pointsTowards(Hypercomplex other) {
		Hypercomplex c = other.plus(partInDirection(other));
		if (c.length() > other.length() && c.phi() == other.phi()) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * Returns the vector with the contribution of this vector in direction of the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector in direction of the provided vector
	 */
	public Complex partInDirection(Hypercomplex r) {
		return Complex.complex(r.times(r.dot(this) / r.dot()));
	}

	/**
	 * Returns the vector with the contribution of this vector orthogonally to the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector orthogonally to the provided vector
	 */
	public Complex partOrthogonallyTo(Hypercomplex r) {
		return minus(partInDirection(r));
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
		ArrayList<Hypercomplex> result = new ArrayList<Hypercomplex>();
		result.add(partInDirection(r));
		result.add(r.minus(result.get(0)));
		return result;
	}

	/**
	 * Returns this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r))
	 */
	public Complex mirroredRadialTo(Hypercomplex r) {
		return this.minus(partInDirection(r).times(2));
	}

	/**
	 * Returns this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r))
	 */
	public Complex mirroredOrthogonalTo(Hypercomplex r) {
		return partInDirection(r).times(2).minus(this);
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
		return phi();
	}
	
	/**
	 * Returns the length r for the Z = r * e^(phi * i) equation (with positive r).
	 * @return the length r for the Z = r * e^(phi * i) equation (with positive r)
	 */
	public double eulerLength() {
		return r();
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
	public Complex sin() {
		return new Complex(Math.sin(re()) * Math.cosh(im()), Math.cos(re()) * Math.sinh(im()));
	}
	
	/**
	 * cosine
	 * @return cosine
	 */
	public Complex cos() {
		return new Complex(Math.cos(re()) * Math.cosh(im()), -Math.sin(re()) * Math.sinh(im()));
	}

	/**
	 * inverse sine
	 * @return inverse sine
	 */
	public Complex asin() {
		double arg1 = Math.sqrt(Math.pow(re() * re() + im() * im() - 1, 2) + 4 * im() * im());
		double arg2 = re() * re() + im() * im();
		return new Complex(Math.signum(re()) / 2 * Math.acos(arg1 - arg2),
				Math.signum(im()) / 2 * acosh(arg1 + arg2));
	}

	/**
	 * inverse cosine
	 * @return inverse cosine
	 */
	public Complex acos() {
		return asin().times(-1).plus(new Complex(Math.PI / 2, 0));
	}

	/**
	 * inverse tangent
	 * @return inverse tangent
	 */
	public Complex atan() {
		return times(this).plus(ONE).pow(-0.5d).acos();
		/*if (re() != 0) {
			return new Complex((Math.atan((re()*re()+im()*im()-1)/(2*re())+Math.PI/2*Math.signum(re())))/2);
		} else if (Math.abs(im()) > 1) {
			return new Complex(Math.PI / 2 * Math.signum(im()));
		} else {
			return new Complex(0);
		}*/
	}

	/**
	 * inverse cotangent
	 * @return inverse cotangent
	 */
	public Complex acot() {
		return new Complex(Math.PI / 2).minus(atan());
	}

	/**
	 * inverse secant
	 * @return inverse secant
	 */
	public Complex asec() {
		return inverse().acos();
	}

	/**
	 * inverse cosecant
	 * @return inverse cosecant
	 */
	public Complex acsc() {
		return inverse().asin();
	}

	/**
	 * hyperbolic sine
	 * @return hyperbolic sine
	 */
	public Complex sinh() {
		return new Complex(Math.sinh(re()) * Math.cos(im()), Math.cosh(re()) * Math.sin(im()));
	}

	/**
	 * hyperbolic cosine
	 * @return hyperbolic cosine
	 */
	public Complex cosh() {
		return new Complex(Math.cosh(re()) * Math.cos(im()), Math.sinh(re()) * Math.sin(im()));
	}

	/**
	 * inverse hyperbolic sine
	 * @return inverse hyperbolic sine
	 */
	public Complex asinh() {
		Complex sqrt = times(this).plus(ONE).pow(0.5);
		if (sqrt == null) {
			return null;
		}
		return plus(sqrt).ln();
	}

	/**
	 * inverse hyperbolic cosine
	 * @return inverse hyperbolic cosine
	 */
	public Complex acosh() {
		Complex sqrt = times(this).minus(ONE).pow(0.5);
		if (sqrt == null) {
			return null;
		}
		return plus(sqrt).ln();
	}

	/**
	 * inverse hyperbolic tangent
	 * @return inverse hyperbolic tangent
	 */
	public Complex atanh() {
		if (Math.abs(re()) >= 1) {
			return null;
		} else {
			return plus(ONE).by(ONE.minus(this)).ln().by(2);
		}
	}
	
}
