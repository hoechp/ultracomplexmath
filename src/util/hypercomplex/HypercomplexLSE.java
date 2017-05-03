package util.hypercomplex;

import java.util.ArrayList;

public class HypercomplexLSE {
	
	private boolean complex = false;
	private boolean binary = false;
	private boolean dual = false;
	private boolean solved = false;
	private int numEquations = 0;
	private int numVariables = 0;
	private ArrayList<ArrayList<Hypercomplex>> complexData = null;
	private ArrayList<ArrayList<Binary>> binaryData = null;
	private ArrayList<ArrayList<Dual>> dualData = null;
	
	/**
	 * Example:<br>
	 * a1 * x + b1 * y = s1,<br>
	 * a2 * x + b2 * y = s2.<p>
	 * HypercomplexLSE lse = new HypercomplexLSE("c", 2,<br>
	 * new Complex(a1), new Complex(b1), new Complex(s1),<br>
	 * new Complex(a2), new Complex(b2), new Complex(s2));
	 * @param type string starting with "c" or "C" for complex data, "b" or "B" for binary data, "d" or "D" for dual data
	 * @param numVariables number of variables to find
	 * @param data list of parameters
	 */
	public HypercomplexLSE(String type, int numVariables, Hypercomplex... data) {
		setComplex(setBinary(setDual(false)));
		if (data.length % (numVariables + 1) != 0) {
			return;
		}
		int numEquations = data.length / (numVariables + 1);
		if (type.startsWith("c") || type.startsWith("C")) {
			this.setNumEquations(numEquations);
			this.setNumVariables(numVariables);
			setComplex(true);
			setComplexData(new ArrayList<ArrayList<Hypercomplex>>());
			for (int equ = 0; equ < numEquations; ++equ) {
				getComplexData().add(new ArrayList<Hypercomplex>());
				for (int var = 0; var <= numVariables; ++var) {
					getComplexData().get(equ).add(data[equ * (numVariables + 1) + var]);
				}
			}
		} else if (type.startsWith("b") || type.startsWith("B")) {
			this.setNumEquations(numEquations);
			this.setNumVariables(numVariables);
			setBinary(true);
			setBinaryData(new ArrayList<ArrayList<Binary>>());
			for (int equ = 0; equ < numEquations; ++equ) {
				getBinaryData().add(new ArrayList<Binary>());
				for (int var = 0; var <= numVariables; ++var) {
					getBinaryData().get(equ).add(Binary.binary(data[equ * (numVariables + 1) + var]));
				}
			}
		} else if (type.startsWith("d") || type.startsWith("D")) {
			this.setNumEquations(numEquations);
			this.setNumVariables(numVariables);
			setDual(true);
			setDualData(new ArrayList<ArrayList<Dual>>());
			for (int equ = 0; equ < numEquations; ++equ) {
				getDualData().add(new ArrayList<Dual>());
				for (int var = 0; var <= numVariables; ++var) {
					getDualData().get(equ).add(Dual.dual(data[equ * (numVariables + 1) + var]));
				}
			}
		} else {
			return;
		}
	}
	
	private static String codeString(Hypercomplex... data) {
		if (data.length > 0 && data[0].isComplex()) {
			return "complex";
		} else if (data.length > 0 && data[0].isBinary()) {
			return "binary";
		} else if (data.length > 0 && data[0].isDual()) {
			return "dual";
		} else {
			return "unknown";
		}
	}

	public HypercomplexLSE(int numVariables, Hypercomplex... data) {
		this(codeString(data), numVariables, data);
	}
	
	private static Hypercomplex[] doubleToHypercomplex(double... arr) {
		Hypercomplex[] result = new Hypercomplex[arr.length];
		for (int i = 0; i < arr.length; ++i) {
			result[i] = new Complex(arr[i]);
		}
		return result;
	}
	
	public HypercomplexLSE(int numVariables, double... data) {
		this("complex", numVariables, doubleToHypercomplex(data));
	}
	
	public void solve() {
		if (numEquations < numVariables) {
			// no need to even try, because this system is for constant hyper-complex solutions, not formulas
			return;
		}
		/**
		 * Gauss's method, column by column -> as soon as it becomes impossible, it's over
		 */
		if (isComplex()) {
			for (int var = 0; var < numVariables; ++var) {
				int index = var;
				while (index < numEquations - 1 && complexData.get(index).get(var).equals(Complex.ZERO)) {
					++index;
				}
				if (index != var) {
					ArrayList<Hypercomplex> storeEquation = complexData.get(var);
					complexData.set(var, complexData.get(index));
					complexData.set(index, storeEquation);
				}
				if (complexData.get(var).get(var).equals(Complex.ZERO)) {
					// there's no way to continue to try
					return;
				}
				// 1. normalize equation so that .get(var) == 1
				Hypercomplex factor = complexData.get(var).get(var).inverse();
				for (int i = 0; i <= numVariables; ++i) {
					complexData.get(var).set(i, complexData.get(var).get(i).times(factor));
				}
				// 2. subtract from all other equations, so there's .get(var) == 0
				for (int i = 0; i < numEquations; ++i) {
					if (i == var) {
						continue;
					}
					factor = complexData.get(i).get(var).times(-1);
					for (int j = 0; j <= numVariables; ++j) {
						complexData.get(i).set(j, complexData.get(i).get(j).plus(complexData.get(var).get(j).times(factor)));
					}
				}
			}
			int count = numEquations - numVariables;
			for (int i = 0; i < count; ++i) {
				// finally check if unused equations are still valid
				int index = complexData.size() - 1;
				Hypercomplex sum = Complex.ZERO;
				for (int j = 0; j < numVariables; ++j) {
					sum.add(complexData.get(index).get(j).times(complexData.get(j).get(numVariables)));
				}
				if (!sum.equals(complexData.get(index).get(numVariables))) {
					return;
				}
				complexData.remove(index);
				--numEquations;
			}
		}
		if (isBinary()) {
			for (int var = 0; var < numVariables; ++var) {
				int index = var;
				while (index < numEquations - 1 && binaryData.get(index).get(var).equals(Binary.ZERO)) {
					++index;
				}
				if (index != var) {
					ArrayList<Binary> storeEquation = binaryData.get(var);
					binaryData.set(var, binaryData.get(index));
					binaryData.set(index, storeEquation);
				}
				if (binaryData.get(var).get(var).equals(Binary.ZERO)) {
					// there's no way to continue to try
					return;
				}
				// 1. normalize equation so that .get(var) == 1
				Binary factor = binaryData.get(var).get(var).inverse();
				for (int i = 0; i <= numVariables; ++i) {
					binaryData.get(var).set(i, binaryData.get(var).get(i).times(factor));
				}
				// 2. subtract from all subsequent equations, so there's .get(var) == 0
				for (int i = var + 1; i < numEquations; ++i) {
					factor = binaryData.get(i).get(var).times(-1);
					for (int j = 0; j <= numVariables; ++j) {
						binaryData.get(i).set(j, binaryData.get(i).get(j).plus(binaryData.get(var).get(j).times(factor)));
					}
				}
			}
			int count = numEquations - numVariables;
			for (int i = 0; i < count; ++i) {
				// finally check if unused equations are still valid
				int index = binaryData.size() - 1;
				Binary sum = Binary.ZERO;
				for (int j = 0; j < numVariables; ++j) {
					sum.add(binaryData.get(index).get(j).times(binaryData.get(j).get(numVariables)));
				}
				if (!sum.equals(binaryData.get(index).get(numVariables))) {
					return;
				}
				binaryData.remove(index);
				--numEquations;
			}
		}
		if (isDual()) {
			for (int var = 0; var < numVariables; ++var) {
				int index = var;
				while (index < numEquations - 1 && dualData.get(index).get(var).equals(Dual.ZERO)) {
					++index;
				}
				if (index != var) {
					ArrayList<Dual> storeEquation = dualData.get(var);
					dualData.set(var, dualData.get(index));
					dualData.set(index, storeEquation);
				}
				if (dualData.get(var).get(var).equals(Dual.ZERO)) {
					// there's no way to continue to try
					return;
				}
				// 1. normalize equation so that .get(var) == 1
				Dual factor = dualData.get(var).get(var).inverse();
				for (int i = 0; i <= numVariables; ++i) {
					dualData.get(var).set(i, dualData.get(var).get(i).times(factor));
				}
				// 2. subtract from all subsequent equations, so there's .get(var) == 0
				for (int i = var + 1; i < numEquations; ++i) {
					factor = dualData.get(i).get(var).times(-1);
					for (int j = 0; j <= numVariables; ++j) {
						dualData.get(i).set(j, dualData.get(i).get(j).plus(dualData.get(var).get(j).times(factor)));
					}
				}
			}
			int count = numEquations - numVariables;
			for (int i = 0; i < count; ++i) {
				// finally check if unused equations are still valid
				int index = dualData.size() - 1;
				Dual sum = Dual.ZERO;
				for (int j = 0; j < numVariables; ++j) {
					sum.add(dualData.get(index).get(j).times(dualData.get(j).get(numVariables)));
				}
				if (!sum.equals(dualData.get(index).get(numVariables))) {
					return;
				}
				dualData.remove(index);
				--numEquations;
			}
		}
		setSolved(true);
	}

	public boolean isComplex() {
		return complex;
	}

	private void setComplex(boolean complex) {
		this.complex = complex;
	}

	public boolean isBinary() {
		return binary;
	}

	private boolean setBinary(boolean binary) {
		this.binary = binary;
		return binary;
	}

	public boolean isDual() {
		return dual;
	}

	private boolean setDual(boolean dual) {
		this.dual = dual;
		return dual;
	}

	public int getNumEquations() {
		return numEquations;
	}

	private void setNumEquations(int numEquations) {
		this.numEquations = numEquations;
	}

	public int getNumVariables() {
		return numVariables;
	}

	private void setNumVariables(int numVariables) {
		this.numVariables = numVariables;
	}

	public ArrayList<ArrayList<Hypercomplex>> getComplexData() {
		return complexData;
	}

	private void setComplexData(ArrayList<ArrayList<Hypercomplex>> cData) {
		this.complexData = cData;
	}

	public ArrayList<ArrayList<Binary>> getBinaryData() {
		return binaryData;
	}

	private void setBinaryData(ArrayList<ArrayList<Binary>> bData) {
		this.binaryData = bData;
	}

	public ArrayList<ArrayList<Dual>> getDualData() {
		return dualData;
	}

	private void setDualData(ArrayList<ArrayList<Dual>> dData) {
		this.dualData = dData;
	}
	
	public String toString() {
		if (isComplex()) {
			String repr = "";
			for (int i = 0; i < numEquations; ++i) {
				for (int j = 0; j < numVariables; ++j) {
					repr += " + (" + complexData.get(i).get(j) + ") * x_" + j;
				}
				repr += " = " + complexData.get(i).get(numVariables) + "\n";
			}
			return repr;
		}
		if (isBinary()) {
			String repr = "";
			for (int i = 0; i < numEquations; ++i) {
				for (int j = 0; j < numVariables; ++j) {
					repr += " + (" + binaryData.get(i).get(j) + ") * x_" + j;
				}
				repr += " = " + binaryData.get(i).get(numVariables) + "\n";
			}
			return repr;
		}
		if (isDual()) {
			String repr = "";
			for (int i = 0; i < numEquations; ++i) {
				for (int j = 0; j < numVariables; ++j) {
					repr += " + (" + dualData.get(i).get(j) + ") * x_" + j;
				}
				repr += " = " + dualData.get(i).get(numVariables) + "\n";
			}
			return repr;
		}
		return null;
	}


	public boolean isSolved() {
		return solved;
	}


	private void setSolved(boolean solved) {
		this.solved = solved;
	}

}
