package util.hypercomplex;

import java.util.ArrayList;
import java.util.Vector;

import util.basics.Matrix;
import util.basics.Vectors;


/**
 * A dual number much alike a complex number, just with the imaginary unit times itself is zero.<p>
 * A dual number can also be a 3-dimensional angle that holds the relative position and direction
 * of a line in space (s1 + lambda1 * v1) to another line in space (s2 + lambda2 * v2).
 * That angle is counterclockwise around the vector v1 cross v2,
 * with the resulting vector possibly being negated so it points from s1 to s2 rather than the other way.
 * if you would look at the points on both lines that are the closest to each other,
 * and you'd draw a line from the point at line1 to the point at line2, that would be the vector
 * that has the direction around which the angle is measured.<p>
 * A <b>dual angle</b> is a normal angle (the real part) plus an addition shift (the imaginary part).
 * So if you have the angle phi + psi*i from line1 (s1 + lambda1 * v1) to line2 (s2 + lambda2 * v2),
 * that means the second line is rotated by phi counterclockwise around the screw vector
 * (connection between closest points from line1 to line2)
 * and also shifted by psi distance-units in that direction.<p>
 * Functions to manage these situations are partly contained in <i>util.basics.Vectors</i>
 * - namely <i>directedConnectingNormal()</i> to obtain the screw vector and <i>closestPoint()</i>
 * to obtain the closest points, <i>normalize()</i> to obtain a specific normalization for each line in space,
 * among other functions.<p>
 * <i>util.hypercomplex.Dual</i> only contains a function to obtain a dual angle -> <i>Dual.dualangle()</i><br>
 * and a function to move a line by a dual angle along a screw vector -> <i>Dual.transcend()</i>
 * 
 * @author Philipp Kolodziej
 */
public class Dual extends Hypercomplex {
	
	private static final long serialVersionUID = -6665877925020979483L;
	
	/**
	 * dual number equaling the real number ONE
	 */
	public final static Dual ONE = new Dual(1);
	
	/**
	 * dual number equaling the real number ZERO
	 */
	public final static Dual ZERO = new Dual();
	
	/**
	 * dual number equaling the imaginary number I
	 */
	public final static Dual I = new Dual(0, 1);
	
	/**
	 * dual number equaling the real number E
	 */
	public final static Dual E = new Dual(Math.E);
	
	/**
	 * Constructor. Constructs a dual number containing the provided parsable data.
	 * @param parseData the String-representation of the number
	 */
	public Dual(String parseData) {
		setCartesian(parseHypercomplex(parseData).getCartesian());
	}
	
	/**
	 * constructor. constructs a vector containing the cartesian and polynominal values (0, 0).
	 */
	public Dual() {
		super();
		setDual(true);
	}

	/**
	 * Constructor. Constructs a real dual number containing the provided real value.
	 * @param re the real part
	 */
	public Dual(double re) {
		super(re);
		setDual(true);
	}

	/**
	 * Constructor. Constructs a dual number containing the provided values.<br>
	 * <b>Note</b> the provided values will be treated as cartesian values.
	 * @param re the real part
	 * @param im the imaginary part
	 */
	public Dual(double re, double im) {
		super(re, im);
		setDual(true);
	}

	/**
	 * Constructor. Constructs a dual number containing the provided values.<br>
	 * <b>Note</b> the provided values will probably* be treated as polynominal values.
	 * As there can be only one constructor with two double values this is the alternative
	 * to construct a dual number with given polynominal parameters.<br>
	 * *To achieve that the data is treated as polynominal the format String
	 * must not contain either the letter "c" or "C" (for cartesian, what it then would be).
	 * @param r the length (if format does not contain "c" or "C", else: the real part)
	 * @param phi the angle (if format does not contain "c" or "C", else: the imaginary part)
	 */
	public Dual(String format, double r, double phi) {
		super(format, r, phi);
		setDual(true);
	}

	/**
	 * Converts Complex into Dual
	 * @param c the complex number to convert
	 * @return the dual number
	 */
	public static Dual dual(Hypercomplex c) {
		return new Dual(c.re(), c.im());
	}
	
	/**
	 * Binary exponential function. Returns e^x with x being the dual exponent.
	 * @param x the binary exponent
	 * @return e^x with x being the binary exponent
	 */
	public static Dual exp(Hypercomplex x) {
		return E.pow(x);
	}

	/**
	 * Dual natural logarithm. Returns ln(x) with x being the dual argument.
	 * @param x the dual argument
	 * @return ln(x) with x being the dual argument
	 */
	public static Dual ln(Hypercomplex x) {
		return dual(x).ln();
	}

	/**
	 * Dual logarithm of x to the base of b.
	 * Returns log_b(x) with x being the dual argument, b being the dual base.
	 * @param b the dual base
	 * @param x the dual argument
	 * @return log_b(x) with x being the dual argument, b being the dual base
	 */
	public static Dual log(Hypercomplex b, Hypercomplex x) {
		return dual(x).log(b);
	}

	/**
	 * Dual power. Returns x to the power of w.
	 * @param x the dual base
	 * @param w the dual exponent
	 * @return x to the power of w
	 */
	public static Dual pow(Hypercomplex x, Hypercomplex w) {
		return dual(x).pow(w);
	}

	/**
	 * Dual power. Returns x to the power of w.
	 * @param x the dual base
	 * @param w the real exponent
	 * @return x to the power of w
	 */
	public static Dual pow(Hypercomplex x, double w) {
		return dual(x).pow(w);
	}

	/**
	 * Principal value of the dual square root. Returns the principal square root of x.
	 * @param x the provided dual number
	 * @return the principal square root of x
	 */
	public static Dual sqrt(Hypercomplex x) {
		return dual(x).pow(0.5);
	}

	/**
	 * the real part is the directional angle and the imaginary part is the length of the connecting common normal.
	 * the angle is denoted as counterclockwise around to the normal from line 1 to line 2.
	 * the distance is also directional but since definition it is denoted as from line 1 towards line 2,
	 * so it can only be positive. treating the distance as negative, you need to negate the angle, too, which makes no sense.
	 * @param s1 point in the first line
	 * @param v1 direction of the first line
	 * @param s2 point in the second line
	 * @param v2 direction of the second line
	 * @return the real part is the directional angle and the imaginary part is the length of the connecting common normal.
	 */
	public static Dual dualAngle(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		if (s1.size() != 3 || v1.size() != 3 || s2.size() != 3 || v2.size() != 3) {
			return null;
		}
		double phi = Vectors.absoluteAngle(v1, v2);
		double r = Double.NaN;
		if (Math.abs(phi) == 0 || Math.abs(phi) == Math.PI) { // parallel
			r = Vectors.length(Vectors.cross(v1, Vectors.minus(s2, s1))) / Vectors.length(v1);
		} else {
			// angle must be directional
			Vector<Double> cross = Vectors.cross(v1, v2);
			// the normal vector (cross) should be pointing from the layer µ1*v1 + µ2*v2 to the point s2 - s1
			Vector<Double> test = Vectors.partInDirection(Vectors.minus(s2, s1), cross);
			test = Vectors.plus(test, cross);
			boolean turn = false;
			if (Vectors.length(test) >= Vectors.length(cross)
					&& test.get(0) * cross.get(0) >= 0
					&& test.get(1) * cross.get(1) >= 0
					&& test.get(2) * cross.get(2) >= 0) {
			} else {
				turn = true;
				cross = Vectors.times(cross, -1);
			}
			r = Math.abs(Vectors.dot(cross, Vectors.minus(s2, s1))) / Vectors.length(cross);
			/** recalculate the DIRECTIONAL phi. */
			@SuppressWarnings("unchecked")
			Vector<Double> proj = Vectors.fromBase(v2, v1, Vectors.times(Vectors.cross(Vectors.cross(v1, v2), v1), -1), Vectors.cross(v1, v2));
			Complex p = new Complex(proj.get(0), proj.get(1));
			phi = p.phi();
			if (turn) {
			} else {
				phi = -phi;
			}
		}
		return new Dual(phi, r);
	}
	
	@SuppressWarnings("unchecked")
	public static void transcend(Vector<Double> s, Vector<Double> v, Vector<Double> screw, Dual angle) {
		Matrix rot = Matrix.getMatrix3D(screw, true, angle.re());
		Matrix shift = Matrix.getMatrix3D(screw, false, angle.im());
		Matrix s2 = new Matrix(s);
		Matrix v2 = new Matrix(v);
		s2 = s2.plus(shift);
		v2 = v2.times(rot);
		Vectors.change(s, s2.getVector());
		Vectors.change(v, v2.getVector());
	}
	
	/**
	 * Returns the projection to the unit sphere of the dual number a + b*epsilon
	 * represented as (x = a, y = b, z = -1) in respect to the unit sphere's north pole (0, 0, 1) -
	 * so the connection between those points intersects the unit sphere at the projected point. 
	 * @return the projected point
	 */
	public Vector<Double> unitSpherePosition() {
		double lambda = 4 / (x() * x() + y() * y() + 4);
		Vector<Double> p = new Vector<Double>();
		p.add(0 + lambda * x());
		p.add(0 + lambda * y());
		p.add(1 + lambda * -2);
		return p;
	}
	
	/**
	 * Returns the dual number that is projected from the unit sphere's north pole
	 * (x = 0, y = 0, z = 1) over the given sphere point onto the dual plane at z = -1.
	 * @param p the projecting point on the unit sphere
	 * @return the projected dual number
	 */
	public static Dual fromUnitSpherePosition(Vector<Double> p) {
		double lambda = 2 / (1 - p.get(2));
		return new Dual(lambda * p.get(0), lambda * p.get(1));
	}
	
	/**
	 * Returns a vector that is the sum of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the sum of this vector and the given vector
	 */
	public Dual plus(Hypercomplex other) {
		return new Dual(re() + other.re(), im() + other.im());
	}

	/**
	 * Returns a vector that is the difference of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the difference of this vector and the given vector
	 */
	public Dual minus(Hypercomplex other) {
		return new Dual(re() - other.re(), im() - other.im());
	}

	/**
	 * Returns a vector that is the product of this vector and the given factor.
	 * @param factor the factor
	 * @return a vector that is the product of this vector and the given factor
	 */
	public Dual times(double factor) {
		return new Dual(re() * factor, im() * factor);
	}

	/**
	 * Returns a vector that is the quotient of this vector and the given divisor.
	 * @param divisor the divisor
	 * @return a vector that is the quotient of this vector and the given divisor
	 */
	public Dual by(double divisor) {
		return new Dual(re() / divisor, im() / divisor);
	}

	/**
	 * Returns a dual number that is the (dual) inverse of this dual number.
	 * @return a dual number that is the (dual) inverse of this dual number
	 */
	public Dual inverse() {
		return conjugate().by(det());
	}

	/**
	 * Returns a dual number that is the dual conjugate of this dual number.
	 * @return a dual number that is the dual conjugate of this dual number
	 */
	public Dual conjugate() {
		return new Dual(re(), -im());
	}

	/**
	 * Returns an ArrayList of the n dual numbers that are the n-th roots of this dual number.
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return an ArrayList of the n dual numbers that are the n-th roots of this dual number
	 */
	public ArrayList<? extends Hypercomplex> roots(int n) {
		return pow(1, n);
	}

	/**
	 * Returns an ArrayList of the n dual numbers that are this to the power of (a / n).
	 * @param a the numerator
	 * @param n the denominator
	 * @return an ArrayList of the n dual numbers that are this to the power of (a / n)
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
		ArrayList<Dual> result = new ArrayList<Dual>();
		Dual base = pow(a);
	    if (n % 2 == 0) {
	    	// type a^(1/n) == +-abs(a)^(1/n), +-E(abs(a)^(1/n)) <-- if d == 1, else its n.def.
	    	double r = Math.abs(base.re());
	    	double d = Math.signum(base.re());
	    	if (d != 1) {
	    		return null;
	    	} else {
	    		double phi = base.im() / base.re();
	    		Dual res1 = new Dual(0, phi / n).exp().times(Math.pow(r, 1d / n));
	    		result.add(res1);
	    		result.add(res1.times(-1));
	    		return result;
	    	}
	    } else {
	    	// type a^(1/n) == sign(a) * abs(a)^(1/n)
	    	double r = Math.abs(base.re());
	    	double d = Math.signum(base.re());
    		double phi = base.im() / base.re();
    		result.add(new Dual(0, phi / n).exp().times(Math.pow(r, 1d / n)).times(d));
    		return result;
	    }
	}
	
	/**
	 * Returns a binary number that is this dual number to the power p.
	 * @param p the power
	 * @return a binary number that is this dual number to the power p
	 */
	public Dual pow(double p) {
		return pow(new Dual(p, 0));
	}
	
	/**
	 * Returns the value of e to the power of this dual number.
	 * @return the value of e to the power of this dual number
	 */
	public Dual exp() {
		return new Dual(1, im()).times(Math.exp(re()));
	}
	
	/**
	 * Returns the natural logarithm of this dual number.
	 * @return the natural logarithm of this dual number
	 */
	public Dual ln() {
		return new Dual(Math.log(re()), im() / re());
	}
	
	/**
	 * Dual logarithm of this to the base of b.
	 * Returns log_b(this) with b being the dual base.
	 * @param b the dual base
	 * @return log_b(this) with b being the dual base
	 */
	public Dual log(Hypercomplex b) {
		Dual result = ln().by(b.ln());
		Dual principalHolder = new Dual("p", 0, result.im());
		result.setImaginary(principalHolder.phi());
		return result;
	}
	
	/**
	 * Returns the value of this dual number to the power of the other provided dual exponent.
	 * @param w the dual exponent
	 * @return the value of this dual number to the power of the other provided dual exponent
	 */
	public Dual pow(Hypercomplex w) { // z^w = exp(log(z) * w) = exp(a) * exp(b * i)
		if (re() <= 0) {
			if (w.isRealInteger()) {
				if ((int)Math.abs(w.re()) % 2 == 0) {
					// positive (re())^(w.re())
					return new Dual(Math.pow(-re(), w.re()), Math.pow(-re(), w.re()) * (im() * w.re() / re()));
				} else {
					// negative (re())^(w.re())
					return new Dual(-Math.pow(-re(), w.re()), -Math.pow(-re(), w.re()) * (im() * w.re() / re()));
				}
			}
			//System.err.println("invalid dual power operation (" + this + ")^(" + w + "): " +
			//		"base needs to have real part > 0 (or exponent needs to be integer without imaginary part)");
			return null;
		}
		return new Dual(Math.pow(re(), w.re()), Math.pow(re(), w.re()) * (Math.log(re()) * w.im() + im() * w.re() / re()));
	}

	/**
	 * Returns true if this dual number is the natural logarithm of the other dual number
	 * @param other the other dual number
	 * @return true if this dual number is the natural logarithm of the other dual number, otherwise false
	 */
	public boolean isLn(Hypercomplex other) {
		return other.ln().equals(this);
	}

	/**
	 * Returns true if this dual number is the
	 * logarithm to the provided base of the other dual number
	 * @param base the dual base
	 * @param other the other dual number
	 * @return true if this dual number is the
	 * logarithm to the provided base of the other dual number, otherwise false
	 */
	public boolean isLog(Hypercomplex base, Hypercomplex other) {
		return other.log(base).equals(this);
	}

	/**
	 * Returns true if this dual number is the dual number that is x to the power of w<br>
	 * <b>Note</b> that if the exponent is real there are infinite solutions,
	 * using the function isPow(Complex x, int a, int n) however checks for a finite number of solutions.
	 * @param x the dual base
	 * @param w the dual exponent
	 * @return true if this dual number is the dual number that is x to the power of w
	 */
	public boolean isPow(Hypercomplex x, Hypercomplex w) {
		return x.pow(w).equals(this);
	}

	/**
	 * Returns true if this is x to the power of (a / n).
	 * @param x the dual base
	 * @param a the numerator of the exponent
	 * @param n the denominator of the exponent
	 * @return true if this is x to the power of (a / n) otherwise false
	 */
	public boolean isPow(Hypercomplex x, int a, int n) {
		return dual(x).pow(a, n).contains(this);
	}

	/**
	 * Returns true if this is the n-th root of x.
	 * @param x the dual base
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return true if this is the n-th root of x otherwise false
	 */
	public boolean isRoot(Hypercomplex x, int n) {
		return dual(x).roots(n).contains(this);
	}

	/**
	 * Returns a copy of the vector that is that is turned by the provided angle.
	 * @param rad the (radian) angle
	 * @return a copy of the vector that is that is turned by the provided angle
	 */
	public Dual turnedBy(double rad) {
		return dual(turnedBy(rad));
	}
	
	/**
	 * Returns a copy of this vector with the length of 1.
	 * @return a copy of this vector with the length of 1
	 */
	public Dual r0() {
		return by(length());
	}
	
	/**
	 * Returns a copy of this vector with the length of the old length to the power of n.
	 * @param n the power
	 * @return a copy of this vector with the length of the old length to the power of n
	 */
	public Dual r(double n) {
		return times(Math.pow(r(), n) / length());
	}

	/**
	 * Returns the vector with the contribution of this vector in direction of the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector in direction of the provided vector
	 */
	public Dual partInDirection(Hypercomplex r) {
		return dual(r).times(r.dot(this) / r.dot());
	}

	/**
	 * Returns the vector with the contribution of this vector orthogonally to the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector orthogonally to the provided vector
	 */
	public Dual partOrthogonallyTo(Hypercomplex r) {
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
		ArrayList<Dual> result = new ArrayList<Dual>();
		result.add(partInDirection(r));
		result.add(dual(r).minus(result.get(0)));
		return result;
	}

	/**
	 * Returns this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r))
	 */
	public Dual mirroredRadialTo(Hypercomplex r) {
		return this.minus(partInDirection(r).times(2));
	}

	/**
	 * Returns this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r))
	 */
	public Dual mirroredOrthogonalTo(Hypercomplex r) {
		return partInDirection(r).times(2).minus(this);
	}

	/**
	 * Returns a dual number that is the (dual) product of this dual number and the given dual factor.
	 * @param f the (dual) factor
	 * @return a dual number that is the (dual) product of this dual number and the given dual factor
	 */
	public Dual times(Hypercomplex f) {
		return new Dual(re() * f.re(), re() * f.im() + im() * f.re());
	}

	/**
	 * Returns a dual number that is the (dual) quotient of this dual number and the given dual divisor.
	 * @param d the (dual) divisor
	 * @return a dual number that is the (dual) quotient of this dual number and the given dual divisor
	 */
	public Dual by(Hypercomplex d) {
		return times(d.inverse());
	}

	/**
	 * Returns the determinant of this dual number.
	 * @return the determinant of this dual number
	 */
	public double det() {
		return re() * re();
	}

	/**
	 * Returns a String representing this dual number.
	 * @return a String representing this dual number
	 */
	@Override
	public String toString() {
		return getCartesian().toString('ê');
	}

	/**
	 * Returns the angle phi for the Z = r * e^(phi * i) equation (potentially negative r).
	 * @return the angle phi for the Z = r * e^(phi * i) equation (potentially negative r)
	 */
	public double eulerAngle() {
		if (re() == 0) {
			return Double.NaN;
		}
		return im() / re();
	}
	
	/**
	 * Returns the length r for the Z = r * d * e^(phi * i) equation (potentially negative r).
	 * @return the length r for the Z = r * d * e^(phi * i) equation (potentially negative r)
	 */
	public double eulerLength() {
		return re();
	}

	// ------------------------- MERE SETTER FUNCTIONS (USING OTHER METHODS) -------------------------

	/**
	 * Multiplies this vector with the given factor (changing its value).
	 * @param factor the factor
	 */
	public void multiply(double factor) {
		set(times(factor));
	}

	/**
	 * Divides the given vector to this vector (changing its value).
	 * @param divisor the divisor
	 */
	public void divide(double divisor) {
		set(by(divisor));
	}

	// ------------------------- TRIGONOMETRIC FUNCTIONS -------------------------
	
	/**
	 * sine
	 * @return sine
	 */
	public Dual sin() {
		return new Dual(Math.sin(re()), Math.cos(re()) * im());
	}

	/**
	 * cosine
	 * @return cosine
	 */
	public Dual cos() {
		return new Dual(Math.cos(re()), -Math.sin(re()) * im());
	}

	/**
	 * hyperbolic sine
	 * @return hyperbolic sine
	 */
	public Dual sinh() {
		return new Dual(Math.sinh(re()), Math.cosh(re()) * im());
	}

	/**
	 * hyperbolic cosine
	 * @return hyperbolic cosine
	 */
	public Dual cosh() {
		return new Dual(Math.cosh(re()), Math.sinh(re()) * im());
	}

	// sin(a, b) = sin(a), cos(a) * b => asin(a, b) = asin(a), b / cos(asin(a))
	/**
	 * inverse sine
	 * @return inverse sine
	 */
	public Dual asin() {
		return new Dual(Math.asin(re()), im() / Math.cos(Math.asin(re())));
	}

	/**
	 * inverse cosine
	 * @return inverse cosine
	 */
	public Dual acos() {
		return new Dual(Math.acos(re()), im() / -Math.sin(Math.acos(re())));
	}
	
	// tan = sin / cos, COS(ATAN(X)) == (X^2 + 1)^(-1 / 2) => ATAN(X) == ACOS((X^2 + 1)^(-1 / 2))
	/**
	 * inverse tangent
	 * @return inverse tangent
	 */
	public Dual atan() {
		return times(this).plus(ONE).pow(-0.5d).acos();
	}

	/**
	 * inverse cotangent
	 * @return inverse cotangent
	 */
	public Dual acot() {
		return new Dual(Math.PI / 2).minus(atan());
	}

	/**
	 * inverse secant
	 * @return inverse secant
	 */
	public Dual asec() {
		return inverse().acos();
	}

	/**
	 * inverse cosecant
	 * @return inverse cosecant
	 */
	public Dual acsc() {
		return inverse().asin();
	}

	/**
	 * inverse hyperbolic sine
	 * @return inverse hyperbolic sine
	 */
	public Dual asinh() {
		return new Dual(Hypercomplex.asinh(re()), im() / Math.cosh(Hypercomplex.asinh(re())));
	}

	/**
	 * inverse hyperbolic cosine
	 * @return inverse hyperbolic cosine
	 */
	public Dual acosh() {
		return new Dual(Hypercomplex.acosh(re()), im() / Math.sinh(Hypercomplex.acosh(re())));
	}
	
	/**
	 * inverse hyperbolic tangent
	 * @return inverse hyperbolic tangent
	 */
	public Dual atanh() {
		return plus(ONE).by(ONE.minus(this)).ln().by(2);
	}
	
	
}
