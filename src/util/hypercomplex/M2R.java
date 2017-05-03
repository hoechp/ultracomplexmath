package util.hypercomplex;

import java.util.Formatter;



/**
 * 
 * This class extends the single hyper-complex algebras,<br>
 * so that it can perform most simple computations even between the different algebras<br>
 * like A [plus, minus, times, by] B with A, B hyper-complex.<br>
 * Obviously functions implemented for all hyper-complex algebras and having only one complex argument<br>
 * can be utilized, too. For example e^m, ln(m), sqrt(m), sin(m), conjugate(m), ...<br>
 * Only undefined higher operations between different algebras can not be used this way, yet.<br>
 * The class is kind of dedicated to a short wikipedia page:
 * 
 *   <b><url=http://en.wikipedia.org/wiki/2_%C3%97_2_real_matrices>
 *   2x2 real matrices</url></b><p>
 * 
 * Where they say that you cannot just express the hyper-complex algebras as 2x2-matrices,<br>
 * but you can gain either a complex, split-complex or dual value out of every matrix.<br>
 * the only catch it, that you need to bring the resulting matrices back into the right form<br>
 * to recognize it as the hyper-complex number within one of the three possible hyper-complex planes,<br>
 * that is represented by the matrix.<p>
 * 
 * The class works just as a loose connection between the hyper-complex algebra classes.<p>
 * 
 * After short testing it becomes obvious that associativity is lost when calculating 'interdimensional'.<br>
 * But the 'length' (eulerian length or det(A) respectively sqrt(det(A)) for that matter)<br>
 * is simply the multiplied length.<p>
 * 
 * Also there is no telling what Ê * î is for example. Okay it has a value, but (a + bÊ)(c + dî)
 * could have any dimension. Determining an 'interdimensional' result calls for matrix manipulation
 * and normalization / classification to a hyper-complex number like in this class.
 * 
 * @author hoechp
 *
 */

public class M2R {
	
	private double a, b, c, d;
	private Hypercomplex value;

	public M2R(Hypercomplex value) {
		if (value.isBinary()) {
			// binary number
			a = d = value.re();
			b = c = value.im();
		} else if (value.isDual()) {
			// dual number
			a = d = value.re();
			b = value.im();
			c = 0;
		} else {
			// complex number
			a = d = value.re();
			b = -value.im();
			c = value.im();
		}
		this.value = value;
	}

	public M2R(double a, double b, double c, double d) {
		this.a = a;
		this.b = b;
		this.c = c;
		this.d = d;
		normalize();
	}
	
	public Hypercomplex value() {
		return value;
	}
	
	public double a() { return a; }
	public double b() { return b; }
	public double c() { return c; }
	public double d() { return d; }
	
	public M2R times(M2R m) {
		return new M2R(a * m.a() + b * m.c(),
				a * m.b() + b * m.d(), c * m.a() + d * m.c(), c * m.b() + d * m.d());
	}
	
	public M2R by(M2R m) {
		m = new M2R(m.value().inverse());
		return new M2R(a * m.a() + b * m.c(),
				a * m.b() + b * m.d(), c * m.a() + d * m.c(), c * m.b() + d * m.d());
	}
	
	public M2R plus(M2R m) {
		return new M2R(a + m.a(), b + m.b(), c + m.c(), d + m.d());
	}
	
	public M2R minus(M2R m) {
		return new M2R(a - m.a(), b - m.b(), c - m.c(), d - m.d());
	}
	
	private void normalize() {
		double x = (a + d) / 2;
		a -= x;
		d -= x;
		double p = a * a + b * c;
		if (p > 0) {
			// binary number
			double y = Math.sqrt(p);
			a = d = x;
			b = c = y;
			value = new Binary(x, y);
		} else if (p == 0) {
			// dual number
			a = d = x;
			b = b != 0 ? b : c;
			c = 0;
			value = new Dual(a, b);
		} else {
			// complex number
			double y = Math.sqrt(-p);
			a = d = x;
			b = -y;
			c = y;
			value = new Complex(x, y);
		}
	}
	
	public M2R pow(M2R m) {
		M2R a = new M2R(value().ln()).times(m);
		return new M2R(a.value().exp());
	}
	
	public boolean equals(Object m) {
		if (!(m instanceof M2R)) {
			return false;
		}
		return value().equals(((M2R)m).value());
	}
	
	public String toString() {
		StringBuilder sb = new StringBuilder();
		Formatter formatter = new Formatter(sb);
		String format = "%." + Hypercomplex.DISPLAYED_CIPHER_COUNT + "g"; // g = general, d = decimal, e = scientific, + = sign, ( = ()
		formatter.format("(" + format + ", " + format + "; " + format + ", " + format + ")", a, b, c, d);
		formatter.close();
		return sb.toString();
	}

}
