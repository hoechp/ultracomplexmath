package util.hypercomplex.calculation;

import java.util.HashMap;
import java.util.HashSet;

import util.hypercomplex.Hypercomplex;
import util.hypercomplex.ultracomplex.Ultra;

public class Calculation {

	private CalculationNode root = null;
	
	public static Ultra calculate(String expression) {
		return new Calculation(expression).result();
	}
	
	public Calculation(String expression) {
		parseExpression(expression);
		normalizeCalculation();
	}

	private void normalizeCalculation() {
		if (root == null || root.getOperator() == null) {
			return;
		}
		// here all sorts of things can be applied TODO: apply more rules
		
		// rule #1 (simplify double brackets where ever they are):
		// a * ((b + c))^2 == a * (b + c)^2
		boolean change = true;
		while (change) {
			HashSet<CalculationNode> brackets = findNodes(Operator.BRACKETS);
			change = false;
			for (CalculationNode outer: brackets) {
				CalculationNode inner = outer.getChildren().get(0);
				if (inner.getOperator() != null && inner.getOperator() == Operator.BRACKETS) {
					outer.getChildren().set(0, inner.getChildren().get(0));
					change = true;
					break;
				}
			}
		}
	}

	private HashSet<CalculationNode> findNodes(Operator inQuestion) {
		return findNodes(root, inQuestion);
	}
	private HashSet<CalculationNode> findNodes(CalculationNode searchRoot, Operator inQuestion) {
		HashSet<CalculationNode> result = new HashSet<CalculationNode>();
		if (searchRoot.getOperator() == null) {
			return result;
		}
		if (searchRoot.getOperator() == inQuestion) {
			result.add(searchRoot);
		}
		for (int i = 0; i < searchRoot.getOperator().involvedTerms(); ++i) {
			result.addAll(findNodes(searchRoot.getChildren().get(i), inQuestion));
		}
		return result;
	}

	public Ultra result() {
		if (root == null) {
			return null;
		}
		return root.getValue();
	}
	
	public void parseExpression(String expression) {
		if (expression == null) {
			return;
		}
		CalculationNode newRoot = null;
		OperatorParseData parse = advancedBracketSearch(expression);
		if (parse == null) {
			root = null;
			return;
		}
		if (parse.getOperators() == null) {
			newRoot = new CalculationNode(parse.getValue());
		} else if (parse.getOperators() != null) {
			if (parse.getOperators().length > 0) {
				int count = 0;
				int end = 0;
				double maxRank = -1;
				int winIndex = -1;
				String[] winStrArr = null;
				for (int i = 0; i < parse.getOperators().length; ++i) {
					Operator o = parse.getOperators()[i];
					end += o.involvedTerms();
					String[] strArr = new String[0];
					for (int j = count; j < end; ++j) {
						strArr = append(strArr, parse.getStrings()[j]);
						++count;
					}
					if (o.rank() >= maxRank) {
						maxRank = o.rank();
						winIndex = i;
						winStrArr = strArr;
					}
				}
				newRoot = new CalculationNode(parse.getOperators()[winIndex]);
				for (int i = 0; i < winStrArr.length; ++i) {
					Calculation subCalc = new Calculation(winStrArr[i]);
					newRoot.addChild(subCalc.getRoot());
				}
			} else {
				newRoot = new CalculationNode(parse.getOperators()[0]);
				for (int i = 0; i < parse.getOperators()[0].involvedTerms(); ++i) {
					Calculation subCalc = new Calculation(i == 0 ? parse.getStrings()[0] : parse.getStrings()[1]);
					newRoot.addChild(subCalc.getRoot());
				}
			}
		}
		root = newRoot;
	}

	private Operator[] append(Operator[] opArr, Operator o) {
		Operator[] opArr2 = new Operator[opArr.length + 1];
		for (int j = 0; j < opArr.length; ++j) {
			opArr2[j] = opArr[j];
		}
		opArr2[opArr.length] = o;
		return opArr2;
	}

	private String[] append(String[] strArr, String str) {
		String[] strArr2 = new String[strArr.length + 1];
		for (int j = 0; j < strArr.length; ++j) {
			strArr2[j] = strArr[j];
		}
		strArr2[strArr.length] = str;
		return strArr2;
	}
	
	public OperatorParseData advancedBracketSearch(String expression) {
		boolean isValue = true;
		for (Operator o: Operator.values()) {
			boolean identified = true;
			if (!o.middleSymbol().equals("")) {
				if (!expression.contains(o.middleSymbol())) {
					identified = false;
				}
			}
			if (!o.rightSymbol().equals("")) {
				if (!expression.contains(o.rightSymbol())) {
					identified = false;
				}
			}
			if (!o.leftSymbol().equals("")) {
				if (!expression.contains(o.leftSymbol())) {
					identified = false;
				}
			}
			if (identified) {
				isValue = false;
				break;
			}
		}
		if (isValue) { // (sub-)expression is hyper-complex value
			return new OperatorParseData(new Ultra(Hypercomplex.parseHypercomplexWeak(expression))); // TODO <--------------- ##################
		}
		// expression is composed using operators
		Operator[] opArr = new Operator[0];
		String[] strArr = new String[0];
		int depth = 0;
		HashMap<Operator, Integer> openingPosition = new HashMap<Operator, Integer>();
		for (int i = 0; i < expression.length(); ++i) {
			char charAt = expression.charAt(i);
			if (charAt == '(') {
				++depth;
			}
			if (charAt == ')') {
				--depth;
			}
			if (depth == 0) {
				for (Operator o: Operator.values()) {
					int positionA = o.leftSymbol().equals("") ? -2 : expression.indexOf(o.leftSymbol(), i);
					int positionB = o.middleSymbol().equals("") ? -2 : expression.indexOf(o.middleSymbol(), i);
					int positionC = o.rightSymbol().equals("") ? -2 : expression.indexOf(o.rightSymbol(), i);
					int positionC1 = o.rightSymbol().equals("") ? -2 : expression.lastIndexOf(o.rightSymbol());
					if (!o.leftSymbol().equals("") && o.middleSymbol().equals("") && o.rightSymbol().equals("")) {
						// type "cos x"
						if (positionA == i) {
							String arg = expression.substring(i + o.leftSymbol().length()).trim();
							opArr = append(opArr, o);
							strArr = append(strArr, arg);
						}
					} else if (o.leftSymbol().equals("") && !o.middleSymbol().equals("") && o.rightSymbol().equals("")) {
						// type "x + y"
						if (positionB == i) {
							String arg1 = expression.substring(0, i).trim();
							String arg2 = expression.substring(i + o.middleSymbol().length()).trim();
							if (arg1.equals("") && (o == Operator.PLUS || o == Operator.MINUS)) {
								arg1 = "0";
							}
							opArr = append(opArr, o);
							strArr = append(strArr, arg1);
							strArr = append(strArr, arg2);
						}
					} else if (!o.leftSymbol().equals("") && o.middleSymbol().equals("") && !o.rightSymbol().equals("")) {
						// type "(x)"
						if (positionC == i && opArr.length == 0) {
							if (openingPosition.get(o) != null && openingPosition.get(o) == 0 && i == expression.length() - o.rightSymbol().length()) {
								String arg = expression.substring(1, i).trim();
								opArr = append(opArr, o);
								strArr = append(strArr, arg);
								openingPosition.remove(o);
							}
						}
					} else if (o.leftSymbol().equals("") && o.middleSymbol().equals("") && !o.rightSymbol().equals("")) {
						// type "x!"
						if (positionC1 == i) {
							String arg = expression.substring(0, i).trim();
							opArr = append(opArr, o);
							strArr = append(strArr, arg);
						}
					} else {
						System.err.println("ERROR: fix Calculation.advancedBracketSearch(String)");
					}
				}
			} else if (i == 0) {
				openingPosition.put(Operator.BRACKETS, 0);
			}
		}
		if (opArr.length == 0) {
			return null;
		}
		return new OperatorParseData(opArr, strArr);
	}
	
	public CalculationNode getRoot() {
		return root;
	}
	public void setRoot(CalculationNode root) {
		this.root = root;
	}

	public String parsableString() {
		return root.toString(false, true);
	}
	
	@Override
	public String toString() {
		if (parsableString().equals(result().toString())) {
			return result().toString();
		}
		return parsableString() + " = " + result();
	}
	
}
