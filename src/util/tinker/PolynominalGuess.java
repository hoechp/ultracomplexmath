package util.tinker;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.HypercomplexLSE;

public class PolynominalGuess {
	
	private int maxVariables;
	private HypercomplexLSE lse;
	private Hypercomplex guess;
	
	private static Hypercomplex[] getEquation(int variables, int x, Hypercomplex value) {
		boolean complex = value.isComplex();
		boolean binary = value.isBinary();
		boolean dual = value.isDual();
		Hypercomplex[] result = new Hypercomplex[variables + 1];
		int count = 0;
		for (int i = variables - 1; i >= 0; --i) {
			if (complex)  {
				result[count++] = new Complex(Math.pow(x, i));
			} else if (binary) {
				result[count++] = new Binary(Math.pow(x, i));
			} else if (dual) {
				result[count++] = new Dual(Math.pow(x, i));
			}
		}
		result[variables] = value;
		return result;
	}
	
	private static Hypercomplex[] getEquation(Hypercomplex[][] equations) {
		if (equations.length == 0 || equations[0].length == 0) {
			return null;
		}
		Hypercomplex[] result = new Hypercomplex[equations.length * equations[0].length];
		int count = 0;
		for (int i = 0; i < equations.length; ++i) {
			for (int j = 0; j < equations[i].length; ++j) {
				result[count++] = equations[i][j];
			}
		}
		return result;
	}

	private static Hypercomplex[] doubleToHypercomplex(double... arr) {
		Hypercomplex[] result = new Hypercomplex[arr.length];
		for (int i = 0; i < arr.length; ++i) {
			result[i] = new Complex(arr[i]);
		}
		return result;
	}
	
	public PolynominalGuess(int maxVariables, double... numbers) {
		this(maxVariables, doubleToHypercomplex(numbers));
	}
	
	public PolynominalGuess(double... numbers) {
		this(numbers.length, numbers);
	}
	
	public PolynominalGuess(int maxVariables, Hypercomplex... numbers) {
		this.maxVariables = Math.min(maxVariables, numbers.length);
		Hypercomplex[][] equations = new Hypercomplex[this.maxVariables][];
		for (int i = 0; i < this.maxVariables; ++i) {
			equations[i] = getEquation(this.maxVariables, this.maxVariables - i, numbers[numbers.length - this.maxVariables + i]);
		}
		lse = new HypercomplexLSE(this.maxVariables, getEquation(equations));
		lse.solve();
		guess = lse.getComplexData().get(this.maxVariables - 1).get(this.maxVariables);
	}
	
	public PolynominalGuess(Hypercomplex... numbers) {
		this(numbers.length, numbers);
	}
	
	public Hypercomplex guess() {
		return guess;
	}
	
	@Override
	public String toString() {
		return guess.toString();
	}

}
