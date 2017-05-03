package util.basics;

import java.util.ArrayList;
import java.util.Vector;

import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.HypercomplexLSE;

public class Vectors {

	public static Vector<Double> toNormalAndCompare(Vector<Double> v, Vector<Double> n, Vector<Double> c) {
		return toBase(v, baseFromNormalAndCompare(n, c));
	}
	
	public static Vector<Double> fromNormalAndCompare(Vector<Double> v, Vector<Double> n, Vector<Double> c) {
		return fromBase(v, baseFromNormalAndCompare(n, c));
	}
	

	public static Vector<Double>[] normalAndCompareFromBase(@SuppressWarnings("unchecked") Vector<Double>... b) {
		if (b.length != 3) {
			return null;
		}
		@SuppressWarnings("unchecked")
		Vector<Double>[] result = (Vector<Double>[])new Vector[2];
		result[0] = b[2]; // normal is z
		result[1] = b[0]; // compare is x
		return result;
	}

	public static Vector<Double>[] baseFromNormalAndCompare(Vector<Double> n, Vector<Double> c) {
		if (n == null || c == null) {
			return null;
		}
		@SuppressWarnings("unchecked")
		Vector<Double>[] result = (Vector<Double>[])new Vector[3];
		result[2] = r0(n); // normal becomes z
		result[1] = r0(cross(n, c)); // normal cross compare becomes y
		result[0] = r0(cross(result[1], n)); // y cross z (corrected compare) becomes x
		return result;
	}

	public static double realAngleAroundNormalWithCompare(Vector<Double> vec, Vector<Double> n, Vector<Double> c) {
		Vector<Double> substitute = fromBase(vec, baseFromNormalAndCompare(n, c));
		return Hypercomplex.complex3DAngle(substitute).real();
	}
	
	@SuppressWarnings("unchecked")
	public static Vector<Double> turnedAroundNormal(Vector<Double> vec, Vector<Double> normal, double angle) {
		return new Matrix(vec).times(Matrix.getMatrix3D(normal, true, angle)).getVector();
	}
	
	public static ArrayList<Vector<Double>> base3D() {
		ArrayList<Vector<Double>> result = new ArrayList<Vector<Double>>();
		Vector<Double> x = new Vector<Double>();
		x.add(1d);
		x.add(0d);
		x.add(0d);
		result.add(x);
		Vector<Double> y = new Vector<Double>();
		y.add(0d);
		y.add(1d);
		y.add(0d);
		result.add(y);
		Vector<Double> z = new Vector<Double>();
		z.add(0d);
		z.add(0d);
		z.add(1d);
		result.add(z);
		return result;
	}
	
	public static Vector<Double> zero3D() {
		return zero(3);
	}
	
	public static Vector<Double> vectorFromHypercomplexAngle(Hypercomplex angle) { // only for 3-dim.
		if (angle == null) {
			return null;
		}
		Vector<Double> hypercomplexAngledVector = new Vector<Double>();
		hypercomplexAngledVector.add(angle.cos().x());
		hypercomplexAngledVector.add(angle.sin().x());
		if (angle.isComplex()) {
			/**
			 * complex 3D-angle gives a hyperbolic structure (along z axis)
			 * 
			 * for every hyperbolic angle imPhi,
			 * the unit circle is projected Math.sinh(imPhi) towards z
			 * and stretched by the factor Math.cosh(imPhi).
			 * so the resulting length is Math.sqrt(Math.sinh²(imPhi) + Math.cosh²(imPhi))
			 * 
			 * -> complex imaginary angle is hyperbolic angle (around y, from x)
			 */
			Hypercomplex cZ = new Complex(angle.cos().y(), angle.sin().y());
			hypercomplexAngledVector.add((angle.y() < 0 ? -1 : 1) * cZ.eulerLength());
		}
		if (angle.isDual()) {
			/**
			 * dual 3D-angle gives unit cylinder (along z axis)
			 * without points where x and y are zero and z is nonzero.
			 * 
			 * so it is like a cylinder (z)-prism from the (x, y)-unit circle.
			 * 
			 * -> dual imaginary angle is distance towards z
			 */
			Hypercomplex dZ = new Complex(angle.cos().y(), angle.sin().y());
			hypercomplexAngledVector.add((angle.y() < 0 ? -1 : 1) * dZ.eulerLength());
		}
		if (angle.isBinary()) {
			/**
			 * binary 3D-angle gives 3D unit sphere. the real part is (like always)
			 * the angle around z, from x. the imaginary part is the angle around y, from x
			 * 
			 * -> binary imaginary angle is normal angle around y, from x
			 */
			Hypercomplex bZ = new Complex(angle.cos().y(), angle.sin().y());
			hypercomplexAngledVector.add((new Complex("p", 1, angle.y()).phi() < 0 ? -1 : 1) * bZ.eulerLength());
		}
		/**
		 * the hyper complex numbers hold true that every 3D point can be reached by a dual, binary and complex angle respectively,
		 * applied the the unit vector towards x and multiplied with a scalar factor.
		 * 
		 * only with dual angles y == 0, z != 0 is impossible,
		 * the same with binary x == 0, y == 0, z != 0
		 */
		return hypercomplexAngledVector;
	}
	
	public static Vector<Double> cross(Vector<Double> a, Vector<Double> b) { // only for 3-dim.
		if (a.size() != 3 || b.size() != 3) {
			return null;
		}
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			result.add(a.get((i + 1) % 3) * b.get((i + 2) % 3)
					 - b.get((i + 1) % 3) * a.get((i + 2) % 3));
		}
		return result;
	}
	
	public static Vector<Double> directedConnectingNormal(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		Vector<Double> cross = cross(v1, v2);
		Vector<Double> test = partInDirection(minus(s2, s1), cross);
		test = plus(test, cross);
		if (length(test) >= length(cross)
				&& test.get(0) * cross.get(0) >= 0
				&& test.get(1) * cross.get(1) >= 0
				&& test.get(2) * cross.get(2) >= 0) {
		} else {
			cross = times(cross, -1);
		}
		Dual angle = Dual.dualAngle(s1, v1, s2, v2);
		return times(cross, angle.y() / length(cross));
	}
	
	public static Vector<Double> closestPoint(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		Vector<Double> dirConNorm = directedConnectingNormal(s1, v1, s2, v2);
		s2 = minus(s2, dirConNorm);
		// now its the intersecting-point-problem
		return intersectingPoint(s1, v1, s2, v2); 
	}
	
	public static Vector<Double> intersectingPoint(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		Vector<Double> lambdas = lambda(s1, v1, s2, v2);
		Vector<Double> pos1 = plus(s1, times(v1, lambdas.get(0)));
		return pos1;
	}
	
	public static void normalize(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		Vector<Double> base = closestPoint(s1, v1, s2, v2);
		Vector<Double> screw = directedConnectingNormal(s1, v1, s2, v2);
		change(s1, base);
		change(v1, times(v1, 1 / length(v1)));
		change(s2, plus(base, screw));
		change(v2, times(v2, 1 / length(v2)));
	}
	
	/**
	 * returns lambda1 and lambda2 from (s1 + lambda1 * v1 == s2 + lambda2 * v2) in a Vector<Double>
	 */
	public static Vector<Double> lambda(Vector<Double> s1, Vector<Double> v1, Vector<Double> s2, Vector<Double> v2) { // only for 3-dim.
		HypercomplexLSE lse = new HypercomplexLSE("c", 2,
					new Complex(v1.get(0)), new Complex(-v2.get(0)),		new Complex(s2.get(0) - s1.get(0)),
					new Complex(v1.get(1)), new Complex(-v2.get(1)),		new Complex(s2.get(1) - s1.get(1)),
					new Complex(v1.get(2)), new Complex(-v2.get(2)),		new Complex(s2.get(2) - s1.get(2))
				);
		lse.solve();
		if (lse.isSolved()) {
			Vector<Double> lambda = new Vector<Double>();
			double lambda1 = lse.getComplexData().get(0).get(lse.getNumVariables()).re();
			lambda.add(lambda1);
			double lambda2 = lse.getComplexData().get(1).get(lse.getNumVariables()).re();
			lambda.add(lambda2);
			return lambda;
		} else {
			return null;
		}
	}
	
	public static void change(Vector<Double> from, Vector<Double> to) {
		if (from.size() != to.size()) {
			return;
		} else {
			for (int i = 0; i < from.size(); ++i) {
				from.set(i, to.get(i));
			}
		}
	}
	
	///////////////////////////////////// N-DIMENSIONAL FUNCTIONS //////////////////////////////////////////////

	/**
	 * returns a zero of the specified dimension
	 * @param dim dimension
	 * @return a zero of the specified dimension
	 */
	public static Vector<Double> zero(int dim) {
		Vector<Double> vec = new Vector<Double>();
		for (int i = 0; i < dim; ++i) {
			vec.add(0d);
		}
		return vec;
	}

	/**
	 * simply creates a vector with vector = x.x_0 * b_0 + x.x_1 * b_1 + ... + x.x_n * b_n.
	 * so the vector has factors for the new base in array b. 
	 * @param x the vector to be transfered
	 * @param b array of new base vectors
	 * @return the transfered vector
	 */
	public static Vector<Double> toBase(Vector<Double> x, @SuppressWarnings("unchecked") Vector<Double>... b) {
		if (x.size() != b.length) {
			return null;
		}
		Vector<Double> vec = zero(x.size());
		for (int i = 0; i < x.size(); ++i) {
			Vector<Double> base = by(b[i], length(b[i]));
			vec = plus(vec, times(base, x.get(i)));
		}
		return vec;
	}
	
	/**
	 * transfers the coordinates of x into the directions given in the list of vectors in b.
	 * @param x the vector in question
	 * @param b the system of directions for the new directions
	 * @return a vector with the coordinates of x transferred into the directions given in the list of vectors in b.
	 */
	public static Vector<Double> fromBase(Vector<Double> x, @SuppressWarnings("unchecked") Vector<Double>... b) {
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < x.size(); ++i) {
			double realDim = Double.NaN;
			Vector<Double> dim = b[i];
			Vector<Double> toDim = partInDirection(x, dim);
			Vector<Double> dirDim = plus(dim, toDim);
			if (length(dirDim) >= length(dim)) {
				boolean turn = false;
				for (int j = 0; j < x.size(); ++j) {
					if (dim.get(j) * dirDim.get(j) < 0) {
						turn = true;
						break;
					}
				}
				if (!turn) {
					realDim = length(toDim);
				} else {
					realDim = -length(toDim);
				}
			} else {
				realDim = -length(toDim);
			}
			result.add(realDim);
			x = minus(x, toDim);
		}
		return result;
	}
	
	/**
	 * the part of s in the direction of r
	 * @param s vector s
	 * @param r vector r
	 * @return the part of s in the direction of r
	 */
	public static Vector<Double> partInDirection(Vector<Double> s, Vector<Double> r) {
		return times(r, dot(s, r) / dot(r));
	}

	/**
	 * the part of s orthogonal to r
	 * @param s vector s
	 * @param r vector r
	 * @return the part of s in the direction of r
	 */
	public static Vector<Double> partOrthogonalTo(Vector<Double> s, Vector<Double> r) {
		return minus(s, partInDirection(s, r));
	}
	
	public static double absoluteAngle(Vector<Double> a) {
		Vector<Double> b = new Vector<Double>();
		if (a.size() > 0) {
			b.add(1d);
		}
		for (int i = 1; i < a.size(); ++i) {
			b.add(0d);
		}
		return absoluteAngle(a, b);
	}

	public static double absoluteAngle(Vector<Double> a, Vector<Double> b) {
		return Math.acos(dot(a, b) / length(a) / length(b));
	}
	
	public static double length(Vector<Double> a) {
		return Math.sqrt(dot(a));
	}
	
	public static double dot(Vector<Double> a, Vector<Double> b) {
		if (a.size() != b.size()) {
			return Double.NaN;
		}
		double sum = 0;
		for (int i = 0; i < a.size(); ++i) {
			sum += a.get(i) * b.get(i);
		}
		return sum;
	}

	public static double dot(Vector<Double> a) {
		double sum = 0;
		for (int i = 0; i < a.size(); ++i) {
			sum += a.get(i) * a.get(i);
		}
		return sum;
	}

	public static Vector<Double> plus(Vector<Double> a, Vector<Double> b) {
		if (a.size() != b.size()) {
			return null;
		}
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			result.add(a.get(i) + b.get(i));
		}
		return result;
	}

	public static Vector<Double> minus(Vector<Double> a, Vector<Double> b) {
		if (a.size() != b.size()) {
			return null;
		}
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			result.add(a.get(i) - b.get(i));
		}
		return result;
	}
	
	public static Vector<Double> times(Vector<Double> a, double real) { 
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			result.add(a.get(i) * real);
		}
		return result;
	}
	
	public static Vector<Double> by(Vector<Double> a, double real) { 
		Vector<Double> result = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			result.add(a.get(i) / real);
		}
		return result;
	}
	
	public static Vector<Double> r0(Vector<Double> v) {
		return by(v, length(v));
	}

	public static boolean equals(Vector<Double> a, Vector<Double> b, double eps) {
		if (a.size() != b.size()) {
			return false;
		}
		for (int dim = 0; dim < a.size(); ++dim) {
			if (Math.abs(a.get(dim) - b.get(dim)) > eps) {
				return false;
			}
		}
		return true;
	}
	
	@SuppressWarnings("unchecked")
	public static Vector<Double> copy(Vector<Double> a) {
		return (Vector<Double>)a.clone();
	}
	
}
