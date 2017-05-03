package util.basics;

import java.util.ArrayList;
import java.util.Vector;

/**
 * get rotation/shift-matrices with the getMatrix3D()-function.
 * manage points as a list of 3D-vectors like this: double[][] m = {{x1, y1, z1}, {x2, y2, z2}, ...};
 * then new_m := rot.times(m).plus(shift).
 * @author Philipp Kolodziej
 */

public class Matrix {
  public double[][] m;
  
  /**
   * Gives a rotation-matrix (if rotate == true) or shift-vector respectively,
   * around the given vector respectively in direction of the given vector,
   * by the angle respectively distance that's stored in amount
   * @param dir the direction vector around which to rotate or along which to shift
   * @param rotate true to get a rotation matrix, false to get a shift vector
   * @param amount angle (in radians) or distance
   * @return the specified rotation matrix or shift vector
   */
  public static Matrix getMatrix3D(Vector<Double> dir, boolean rotate, double amount) {
	  dir = Vectors.times(dir, 1 / Vectors.length(dir));
	  double x1 = dir.get(0), x2 = dir.get(1), x3 = dir.get(2);
	  if (rotate) {
		  double c = Math.cos(amount), s = Math.sin(amount);
		  double[][] m1 = {{x1 * x1 * (1 - c) + c, x2 * x1 * (1 - c) + x3 * s, x3 * x1 * (1 - c) - x2 * s},
			                {x1 * x2 * (1 - c) - x3 * s, x2 * x2 * (1 - c) + c, x3 * x2 * (1 - c) + x1 * s},
			                {x1 * x3 * (1 - c) + x2 * s, x2 * x3 * (1 - c) - x1 * s, x3 * x3 * (1 - c) + c}};
		  return new Matrix(m1);
	  } else {
		  double[][] s1 = {{x1 * amount, x2 * amount, x3 * amount}};
		  return new Matrix(s1);
	  }
  }
  
  public static Matrix getMatrix3D(int dim, boolean rotate, double amount) {
	  // rotation matrices and shift vectors
	  if (rotate) {
		  double c = Math.cos(amount), s = Math.sin(amount);
		  if (dim == 0) {
			  double[][] m1 = {{1, 0, 0}, {0, c, s}, {0, -s, c}};
			  return new Matrix(m1);
		  } else if (dim == 1) {
			  double[][] m2 = {{c, 0, -s}, {0, 1, 0}, {s, 0, c}};
			  return new Matrix(m2);
		  } else if (dim == 2) {
			  double[][] m3 = {{c, s, 0}, {-s, c, 0}, {0, 0, 1}};
			  return new Matrix(m3);
		  } else {
			  return null;
		  }
	  } else {
		  if (dim == 0) {
			  double[][] s1 = {{amount, 0, 0}};
			  return new Matrix(s1);
		  } else if (dim == 1) {
			  double[][] s2 = {{0, amount, 0}};
			  return new Matrix(s2);
		  } else if (dim == 2) {
			  double[][] s3 = {{0, 0, amount}};
			  return new Matrix(s3);
		  } else {
			  return null;
		  }
	  }
  }

  public Matrix(@SuppressWarnings("unchecked") Vector<Double>... vals) {
	m = new double[vals.length][3];
	for (int i = 0; i < vals.length; ++i) {
	  for (int j = 0; j < 3; ++j) {
		m[i][j] = vals[i].get(j);
	  }
	}
  }
  public Matrix(int i, int j) {
    m = new double[i][];
    for (int k = 0; k < i; ++k) {
      m[k] = new double[j];
    }
  }
  public Matrix(int i, int j, double... vals) {
	m = new double[i][];
	for (int k = 0; k < i; ++k) {
	  m[k] = new double[j];
	  for (int o = 0; o < j; ++o) {
	    m[k][o] = vals[k * i + o];
	  }
	}
  }
  public Matrix(double[][] m) { this.m = m; }
  public Matrix plus(Matrix other) {
    Matrix solution = new Matrix(other.m.length, other.m[0].length);
    for (int i = 0; i < other.m.length; ++i) {
      for (int j = 0; j < other.m[0].length; ++j) {
        solution.m[i][j] = this.m[i % this.m.length][j % this.m[0].length] + other.m[i][j];
      }
    }
    return solution;
  }
  public Matrix minus(Matrix other) {
    Matrix solution = new Matrix(other.m.length, other.m[0].length);
    for (int i = 0; i < other.m.length; ++i) {
      for (int j = 0; j < other.m[0].length; ++j) {
        solution.m[i][j] = other.m[i][j] - this.m[i % this.m.length][j % this.m[0].length];
      }
    }
    return solution;
  }
  public Matrix times(Matrix other) {
    Matrix solution = new Matrix(this.m.length, other.m[0].length);
    for (int i = 0; i < this.m.length; ++i) {
      for (int j = 0; j < other.m[0].length; ++j) {
        solution.m[i][j] = 0;
        for (int k = 0; k < this.m[0].length; ++k) {
          solution.m[i][j] += this.m[i][k] * other.m[k][j];
        }
      }
    }
    return solution;
  }
  public ArrayList<Vector<Double>> getVectors() {
	  if (m.length == 0) {
		  return null;
	  }
	  ArrayList<Vector<Double>> result = new ArrayList<Vector<Double>>();
	  for (int i = 0; i < m.length; ++i) {
		  Vector<Double> data = new Vector<Double>();
		  for (int j = 0; j < m[i].length; ++j) {
			  data.add(m[i][j]);
		  }
		  result.add(data);
	  }
	  return result;
  }
  public Vector<Double> getVector() {
	  if (m.length == 0) {
		  return null;
	  }
	  Vector<Double> data = new Vector<Double>();
	  for (int j = 0; j < m[0].length; ++j) {
		  data.add(m[0][j]);
	  }
	  return data;
  }
  public Matrix mirror() {
	  Matrix mirror = new Matrix(m[0].length, m.length);
	  for (int i = 0; i < m.length; ++i) {
		  for (int j = 0; j < m[0].length; ++j) {
			  mirror.m[j][i] = m[i][j];
		  }
	  }
	  return mirror;
  }
  public String toString() {
    String solution = "";
    for (int i = 0; i < m.length; ++i) {
      for (int j = 0; j < m[0].length; ++j) {
        solution = solution + "\t" + m[i][j];
      }
      solution = solution + "\n";
    }
    return solution;
  }
}