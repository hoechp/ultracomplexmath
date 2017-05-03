package util.hypercomplex.formula;

import java.util.ArrayList;
import java.util.HashMap;

import util.hypercomplex.ultracomplex.Ultra;

/**
 * Formula plus associated system of Formulas of the Parameter of the Formula plus their Parameter's Formulas and so on.
 * Introduced variables are first set to 0 and can later be set to any Formula. If a Formula isn't referenced anymore, it's deleted.<p>
 * <b>Usage examples:</b><br>
 * FormulaSystem fs = new FormulaSystem("x³ + y");<br>
 * fs.set("x", "cos(phi)");<br>
 * fs.set("y", "3");<br>
 * fs.set("phi", "1/2*pi");<br>
 * Hypercomplex res = fs.result();<p>
 * fs = new FormulaSystem("x³ + y").set("x = cos(phi)").set("y = 3").set("phi = 1/2*pi");<br>
 * res = fs.result();<p>
 * fs = new FormulaSystem("x³ + y").set("x = cos(phi), y = 3, phi = 1/2*pi");<br>
 * res = fs.result();<p>
 * fs = new FormulaSystem("x³ + y, x = cos(phi), y = 3, phi = 1/2*pi");<br>
 * res = fs.result();<p>
 * @author Philipp Kolodziej
 */
public class FormulaSystem {

	String name;
	Formula root;
	HashMap<String, Formula> formula = new HashMap<String, Formula>();
	ArrayList<String> paramFormulaString = new ArrayList<String>();
	ArrayList<Formula> paramFormula = new ArrayList<Formula>();

	@SuppressWarnings("unchecked")
	private void setThis(FormulaSystem other) {
		this.name = other.name;
		this.root = other.root;
		this.formula = (HashMap<String, Formula>)other.formula.clone();
		this.paramFormulaString = (ArrayList<String>)other.paramFormulaString.clone();
		this.paramFormula = (ArrayList<Formula>)other.paramFormula.clone();
	}
	
	public FormulaSystem(String... values) {
		if (values.length == 0) {
			setThis(new FormulaSystem("0", true));
		} if (values.length == 1) {
			String[] split = splitList(values[0]);
			if (split != null) {
				setThis(new FormulaSystem(split));
				return;
			}
			String[] setup = splitCommand(values[0]);
			if (setup == null) {
				setThis(new FormulaSystem(values[0], true));
			} else {
				setThis(new FormulaSystem(setup[0], setup[1], true));
			}
		} if (values.length == 2) {
			String[] setup1 = splitCommand(values[0]);
			String[] setup2 = splitCommand(values[0]);
			if (setup1 == null) {
				if (setup2 == null) {
					setThis(new FormulaSystem(values[0], values[1], true));
				} else {
					setThis(new FormulaSystem(values[0], true));
					set(setup2[0], setup2[1]);
				}
				setThis(new FormulaSystem(values[0], true));
			} else {
				setThis(new FormulaSystem(setup1[0], setup1[1], true));
				set(setup2[0], setup2[1]);
			}
			setThis(new FormulaSystem(values[0], values[1], true));
		} else {
			String[] setup = splitCommand(values[0]);
			if (setup == null) {
				setThis(new FormulaSystem(values[0], true));
			} else {
				setThis(new FormulaSystem(setup[0], setup[1], true));
			}
			for (int i = 1; i < values.length; ++i) {
				String[] command = splitCommand(values[i]);
				if (command != null) {
					set(command[0], command[1]);
				}
			}
		}
	}
	
	private FormulaSystem(String value, boolean useThisConstructor) {
		this("formula", value, true);
	}
	
	private FormulaSystem(String name, String value, boolean useThisConstructor) {
		this.name = name;
		root = new Formula(value);
		for (Parameter param: root.getParameter()) {
			formula.put(param.getIdentifier(), root);
		}
	}

	private String[] splitList(String command) {
		String[] arr = new String[0];
		String[] split = splitListRaw(command);
		while (split != null) {
			String[] newArr = new String[arr.length + 1];
			for (int i = 0; i < arr.length; ++i) {
				newArr[i] = arr[i];
			}
			newArr[newArr.length - 1] = split[0];
			arr = newArr;
			command = split[1];
			split = splitListRaw(command);
		}
		String[] newArr = new String[arr.length + 1];
		for (int i = 0; i < arr.length; ++i) {
			newArr[i] = arr[i];
		}
		newArr[newArr.length - 1] = command;
		arr = newArr;
		return arr.length < 2 ? null : arr;
	}
	
	private String[] splitListRaw(String command) {
		if (!command.contains(",") && !command.contains(";")) {
			return null;
		}
		if (command.contains(",")) {
			int index = command.indexOf(",");
			String key = command.substring(0, index).trim();
			String value = command.substring(index + ",".length()).trim();
			String[] arr = {key, value};
			return arr;
		} else {
			int index = command.indexOf(";");
			String key = command.substring(0, index).trim();
			String value = command.substring(index + ";".length()).trim();
			String[] arr = {key, value};
			return arr;
		}
	}
	
	private String[] splitCommand(String command) {
		if (!command.contains("=") && !command.contains(":=")) {
			return null;
		}
		if (command.contains(":=")) {
			int index = command.indexOf(":=");
			String key = command.substring(0, index).trim();
			String value = command.substring(index + ":=".length()).trim();
			String[] arr = {key, value};
			return arr;
		} else {
			int index = command.indexOf("=");
			String key = command.substring(0, index).trim();
			String value = command.substring(index + "=".length()).trim();
			String[] arr = {key, value};
			return arr;
		}
	}
	
	public FormulaSystem set(String... commands) {
		if (commands.length == 2) {
			if (name.equals(commands[0])) {
				setThis(new FormulaSystem(commands[0], commands[1], true));
				return this;
			} else {
				if (paramFormulaString.contains(commands[0])) {
					int index = -1;
					for (int i = 0; i < paramFormulaString.size(); ++i) {
						if (paramFormulaString.get(i).equals(commands[0])) {
							index = i;
							break;
						}
					}
					deletePath(index);
				}
				Formula parameter = new Formula(commands[1]);
				formula.get(commands[0]).set(commands[0], parameter);
				for (Parameter param: parameter.getParameter()) {
					formula.put(param.getIdentifier(), parameter);
				}
				if (!paramFormulaString.contains(commands[0])) {
					paramFormulaString.add(commands[0]);
					paramFormula.add(parameter);
				}
			}
		} else {
			for (int i = 0; i < commands.length; ++i) {
				String[] command = splitCommand(commands[i]);
				if (command == null) {
					continue;
				}
				set(command[0], command[1]);
			}
		}
		return this;
	}
	
	private void deletePath(int index) {
		ArrayList<Parameter> nextOnesParam = new ArrayList<Parameter>();
		nextOnesParam.addAll(paramFormula.get(index).getParameter());
		ArrayList<String> nextOnesStr = new ArrayList<String>();
		for (Parameter p: nextOnesParam) {
			nextOnesStr.add(p.getIdentifier());
		}
		ArrayList<Integer> nextIndices = new ArrayList<Integer>();
		for (int i = 0; i < paramFormulaString.size(); ++i) {
			if (nextOnesStr.contains(paramFormulaString.get(i))) {
				int toAdd = i > index ? i - 1 : i;
				nextIndices.add(toAdd);
			}
		}
	    for (Parameter p: nextOnesParam) {
			formula.remove(p.getIdentifier());
		}
		paramFormula.remove(index);
		paramFormulaString.remove(index);
		int count = 0;
		for (int i: nextIndices) {
			deletePath(i - count);
			++count;
		}
	}

	public Formula get(String key) {
		if (name.equals(key)) {
			return root;
		}
		return formula.get(key).get(key).getFormula();
	}
	
	public Ultra result() {
		return root.result();
	}
	
	@Override
	public String toString() {
		String result = "";
		for (int i = paramFormula.size() - 1; i >= 0; --i) {
			if (paramFormula.get(i) != root) {
				result += paramFormulaString.get(i) + " = " + paramFormula.get(i) + ", ";
			}
		}
		result += name + " = " + root.toString();
		return result;
	}
	
}
