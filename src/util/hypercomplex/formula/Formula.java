package util.hypercomplex.formula;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import util.hypercomplex.Hypercomplex;
import util.hypercomplex.calculation.Calculation;
import util.hypercomplex.calculation.Operator;
import util.hypercomplex.ultracomplex.Ultra;

/**
 * Formula with Hypercomplex values that can be parsed out of its String-representation.<br>
 * <b>usage example:</b><br>
 * Formula f1 = new Formula("x³ - x");<br>
 * f1.set("x", -1);<br>
 * Formula f2 = new Formula("x³ - cos(phi)^ln(y)");<br>
 * f2.set("x", f1);<br>
 * f2.set("phi", new Complex(0, 2));<br>
 * f2.set("y", "cos(1/2 * pi)²");<br>
 * Hypercomplex result = f2.result();<br>
 * Formula f3 = new Formula("î²"); // complex imaginary unit<br>
 * Formula f4 = new Formula("ê²"); // dual imaginary unit<br>
 * Formula f5 = new Formula("Ê²"); // binary imaginary unit<br>
 * Formula f6 = new Formula("cos(pi)*Ê²");<br>
 * <br>
 * For a full list of usable Operators see enum util.hypercomplex.calculation.Operator<br>
 * The only named constants are pi (or PI, pI, Pi) and e (or E)<br>
 * @author Philipp Kolodziej
 * @see util.hypercomplex.calculation.Operator
 */
public class Formula {

	private Ultra value = null;
	private HashMap<String, Parameter> keyMap = new HashMap<String, Parameter>();
	private String formulaString;
	private ArrayList<Parameter> parameter = new ArrayList<Parameter>();
	private static String[] strArrZero = {};
	private boolean repaired = true;
	
	public Formula(Formula other) {
		this(other.formulaString());
	}	
	public Formula(String expression) {
		this(expression, strArrZero);
	}
	public Formula(Hypercomplex value) {
		this.value = new Ultra(value);
		this.formulaString = value.toString();
	}
	public Formula(Ultra value) {
		this.value = value;
		this.formulaString = value.toString();
	}
	public Formula(Calculation calc) {
		this.formulaString = calc.parsableString();
	}
	public Formula(String formulaString, Parameter p1, Parameter... para) {
		this.formulaString = formulaString;
		parameter.add(p1);
		for (Parameter p: para) {
			parameter.add(p);
			keyMap.put(p.getIdentifier(), p);
		}
		repaired = false;
		repairIfNeeded();
	}
	
	public Formula(String formulaString, String... para) {
		this.formulaString = formulaString;
		for (String s: para) {
			if (keyMap.get(s) == null) {
				Parameter created = new Parameter(s, Ultra.ZERO);
				parameter.add(created);
				keyMap.put(s, created);
			} else {
				parameter.add(keyMap.get(s));
			}
		}
		repaired = false;
		repairIfNeeded();
	}
	
	public HashSet<Parameter> getParameter() {
		return new HashSet<Parameter>(keyMap.values());
	}
	
	public Parameter get(String key) {
		return keyMap.get(key);
	}
	
	public void set(String key, Formula formula) {
		if (keyMap.get(key) != null) {
			keyMap.get(key).setFormula(formula);
		} else {
			keyMap.put(key, new Parameter(key, formula));
		}
	}
	
	public void set(String key, double value) {
		Ultra c = new Ultra(value);
		if (keyMap.get(key) != null) {
			keyMap.get(key).setValue(c);
		} else {
			keyMap.put(key, new Parameter(key, c));
		}
	}
	
	public void set(String key, Ultra value) {
		if (keyMap.get(key) != null) {
			keyMap.get(key).setValue(value);
		} else {
			keyMap.put(key, new Parameter(key, value));
		}
	}
	
	public void set(String key, String value) {
		set(key, Calculation.calculate(value));
	}
	
	private ArrayList<String> split(String str, char splitAt) {
		ArrayList<String> strings = new ArrayList<String>();
		boolean change = true;
		while (change) {
			change = false;
			for (int i = 0; i < str.length(); ++i) {
				if (str.charAt(i) == splitAt) {
					strings.add(str.substring(0, i));
					str = str.substring(i + 1);
					change = true;
					break;
				}
			}
		}
		strings.add(str);
		return strings;
	}
	
	private String parametersStringRepresentation() {
		String result = "";
		for (Parameter p: getParameter()) {
			if (!result.equals("")) {
				result += ", ";
			}
			result += p.toString();
		}
		return result;
	}
	
	public String formulaString() {
		return getStringRepresentation(true);
	}

	private String getStringRepresentation(boolean symbolic) {
		if (!formulaString.contains("?")) {
			return formulaString;
		}
		ArrayList<String> parts = split(formulaString, '?');
		String calc = "";
		int paramCount = 0;
		for (int i = 0; i < parts.size(); ++i) {
			calc += parts.get(i);
			if (i < parts.size() - 1) {
				if (symbolic) {
					calc += parameter.get(paramCount).getIdentifier();
				} else {
					Ultra toWrite = parameter.get(paramCount).getValue();
					if (new Calculation(toWrite.toString()).getRoot().getOperator() != null) {
						calc += "(" + toWrite + ")";
					} else {
						calc += toWrite;
					}
				}
				++paramCount;
			}
		}
		return calc;
	}
	
	private void repairIfNeeded() {
		if (!repaired) {
			repairFormula();
			repaired = true;
		}
	}
	
	private void repairFormula() {
		// mark data that is parsable as part of an Operator
		HashSet<Integer> parsableData = new HashSet<Integer>();
		for (int i = 0; i < formulaString.length(); ++i) {
			for (Operator o: Operator.values()) {
				int posL = o.leftSymbol().equals("") ? -2 : formulaString.indexOf(o.leftSymbol(), i);
				int posM = o.middleSymbol().equals("") ? -2 : formulaString.indexOf(o.middleSymbol(), i);
				int posR = o.rightSymbol().equals("") ? -2 : formulaString.indexOf(o.rightSymbol(), i);
				String sym = null;
				if (posL == i) {
					sym = o.leftSymbol();
				}
				if (posM == i) {
					sym = o.middleSymbol();
				}
				if (posR == i) {
					sym = o.rightSymbol();
				}
				if (sym != null) {
					for (int j = i; j < i + sym.length(); ++j) {
						parsableData.add(j);
					}
					i +=  sym.length() - 1;
					break;
				}
			}
		}
		/* 
		 * find segments between those marked areas to check if they are META ("?")
		 * constant (like "1 + î") or not parsable at all (like "phi")
		 * in which case a parameter with that name is created and set up correctly.
		 */
		ArrayList<String> paramRaw = new ArrayList<String>();
		ArrayList<Integer> paramPosRaw = new ArrayList<Integer>();
		String build = "";
		for (int i = 0; i < formulaString.length(); ++i) {
			if (parsableData.contains(i)) {
				if (build.length() > 0) {
					paramRaw.add(build);
					paramPosRaw.add(i - build.length());
				}
				build = "";
			} else {
				build += formulaString.charAt(i);
			}
		}
		if (build.length() > 0) {
			paramRaw.add(build);
			paramPosRaw.add(formulaString.length() - build.length());
		}
		/*
		 * remove the cases that are parsable as a number or the META-sign "?"
		 */
		ArrayList<String> param = new ArrayList<String>();
		ArrayList<Integer> paramPos = new ArrayList<Integer>();
		for (int i = 0; i < paramRaw.size(); ++i) {
			String key = paramRaw.get(i);
			int index = paramPosRaw.get(i);
			if (!"?".equals(key.trim()) && !"".equals(key.trim())) {
				try {
					Hypercomplex.parseHypercomplexWeakest(key);
				} catch (Throwable t) {
					String innerKey = key.trim();
					int innerIndex = key.indexOf(innerKey);
					key = innerKey;
					index += innerIndex;
					param.add(key);
					paramPos.add(index);
				}
			}
		}
		// now add the parameters and set everything up correctly
		for (int i = 0; i < param.size(); ++i) {
			String key = param.get(i);
			int index = paramPos.get(i);
			String before = formulaString.substring(0, index);
			String after = formulaString.substring(index + key.length());
			String substitute = before + "?" + after;
			formulaString = substitute;
			for (int j = i + 1; j < paramPos.size(); ++j) {
				paramPos.set(j, paramPos.get(j) - key.length() + 1);
			}
			addParamAtParse(key);
		}
	}
	
	public Calculation getCalculation() {
		repairIfNeeded();
		return new Calculation(getStringRepresentation(false));
	}
	
	private void addParamAtParse(String param) {
		if (keyMap.get(param) == null) {
			Parameter created = new Parameter(param, Ultra.ZERO);
			parameter.add(created);
			keyMap.put(param, created);
		} else {
			parameter.add(keyMap.get(param));
		}
	}
	
	public Ultra result() {
		if (value != null) {
			return value;
		}
		return getCalculation().result();
	}

	public String parsableString() {
		return getCalculation().parsableString();
	}
	
	@Override
	public String toString() {
		Calculation calc = getCalculation();
		if (calc.getRoot().getOperator() == null) {
			return calc.getRoot().getValue().toString();
		}
		if (parameter.size() == 0) {
			return calc.toString();
		}
		return getStringRepresentation(true)
			+ " = " + calc.toString();
	}
	
	public String toLongString() {
		Calculation calc = getCalculation();
		if (calc.getRoot().getOperator() == null) {
			return calc.getRoot().getValue().toString();
		}
		if (parameter.size() == 0) {
			return calc.toString();
		}
		return "with " + parametersStringRepresentation() + ": "
			+ getStringRepresentation(true)
			+ " = " + calc.toString();
	}
	
	/**
	 * returns either the normal or debugged formula. debugged means "1 + 2 + 3" will be "((1 + 2) + 3)"
	 * depending on how the calculation is actually stored and therefore computed in this formula
	 * @param debug flag to get the debugging output form (true) or the normal one (false)
	 * @return either the normal or debugged formula
	 */
	public String toString(boolean debug) {
		if (!debug) {
			return toString();
		}
		Calculation calc = getCalculation();
		if (calc.getRoot().getOperator() == null) {
			return calc.getRoot().getValue().toString();
		}
		if (parameter.size() == 0) {
			return calc.getRoot().toString(true, true)
					+ " = " + result();
		}
		return calc.getRoot().toString(true, true) + ", "
			+ getStringRepresentation(true)
			+ " = " + calc.toString();
	}
	
}
