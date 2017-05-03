package util.hypercomplex.calculation;

/**
 * allowed types:
 * 		op x - like "cos x", "RE(x)"
 *      x op - like "x!", "(x)'"
 *      x op y - like "x + y", "10_log(100)"
 * forbidden types:
 * 		opa x opb (except brackets)
 * 		x opa y opb
 * 		opa x opb y
 * 		x opa y opb z
 * 		opa x opb y opc z
 * 		x opa y opb z opc
 * 		x opa y opb z opc phi
 * @author hoechp
 *
 */
public enum Operator {

	// MOST BASIC:
	BRACKETS(0, "(", "", ")", "in brackets", 1, 1),
	TIMES(1, "", "*", "", "times", 2, 2),
	BY(2, "", "/", "", "by", 2, 2),
	PLUS(3, "", "+", "", "plus", 2, 3),
	MINUS(4, "", "-", "", "minus", 2, 3),
	POW(6, "", "^", "", "to the power of", 2, 1),
	EXP(9, "exp", "", "", "e to the power of", 1, 1),
	LN(10, "ln", "", "", "natural logarithm of", 1, 1),
	LOG(11, "", "_log", "", "logarithm", 2, 1.5),
	// TRIGONOMETRY:
	COS(12, "cos", "", "", "cosine", 1, 1),
	ACOS(13, "acos", "", "", "inverse cosine", 1, 1),
	COSH(14, "cosh", "", "", "hyperbolic cosine", 1, 1),
	ACOSH(15, "acosh", "", "", "inverse hyperbolic cosine", 1, 1),
	SIN(16, "sin", "", "", "sine", 1, 1),
	ASIN(17, "asin", "", "", "inverse sine", 1, 1),
	SINH(18, "sinh", "", "", "hyperbolic sine", 1, 1),
	ASINH(19, "asinh", "", "", "inverse hyperbolic sine", 1, 1),
	TAN(20, "tan", "", "", "tangens", 1, 1),
	ATAN(21, "atan", "", "", "inverse tangens", 1, 1),
	TANH(22, "tanh", "", "", "hyperbolic tangens", 1, 1),
	ATANH(23, "atanh", "", "", "inverse hyperbolic tangens", 1, 1),
	COT(24, "cot", "", "", "cotangens", 1, 1),
	ACOT(25, "acot", "", "", "inverse cotangens", 1, 1),
	COTH(26, "coth", "", "", "hyperbolic cotangens", 1, 1),
	ACOTH(27, "acoth", "", "", "inverse hyperbolic cotangens", 1, 1),
	SEC(28, "sec", "", "", "secant", 1, 1),
	ASEC(29, "asec", "", "", "inverse secant", 1, 1),
	SECH(30, "sech", "", "", "hyperbolic secant", 1, 1),
	ASECH(31, "asech", "", "", "inverse hyperbolic secant", 1, 1),
	CSC(32, "csc", "", "", "cosecant", 1, 1),
	ACSC(33, "acsc", "", "", "inverse cosecant", 1, 1),
	CSCH(34, "csch", "", "", "hyperbolic cosecant", 1, 1),
	ACSCH(35, "acsch", "", "", "inverse hyperbolic cosecant", 1, 1),
	// MORE:
	SQRT(36, "sqrt", "", "", "square root of", 1, 1),
	CONJUGATE(41, "conjugate", "", "", "(hyper-)complex conjugate", 1, 1),
	INVERSE(42, "inverse", "", "", "inverse", 1, 1),
	RE(44, "RE", "", "", "real part (hyper-)complex number", 1, 1),
	SQR(53, "", "", "²", "square", 1, 0.5),
	CUB(54, "", "", "³", "cubic", 1, 0.5),
	NEGATE(55, "neg", "", "", "negation", 1, 0.5);
	// ## WHEN ADDING OPERATORS: ALSO CHANGE CalculationNode.internallyComputedResult() !!! ##
	
	private int code;
	private double rank;
	private String symbolLeft;
	private String symbolMiddle;
	private String symbolRight;
	private String command;
	private int involvedTerms;
	
	private Operator(int code, String symbolLeft, String symbolMiddle, String symbolRight, String command, int involvedTerms, double rank) {
		this.code = code;
		this.symbolLeft = symbolLeft;
		this.symbolMiddle = symbolMiddle;
		this.symbolRight = symbolRight;
		this.command = command;
		this.involvedTerms = involvedTerms;
		this.rank = rank;
	}

	public int code() {
		return code;
	}
	public String leftSymbol() {
		return symbolLeft;
	}
	public String middleSymbol() {
		return symbolMiddle;
	}
	public String rightSymbol() {
		return symbolRight;
	}
	public String command() {
		return command;
	}
	public int involvedTerms() {
		return involvedTerms;
	}
	public double rank() {
		return rank;
	}
	
}
