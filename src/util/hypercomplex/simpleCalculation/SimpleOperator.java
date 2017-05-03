package util.hypercomplex.simpleCalculation;

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
public enum SimpleOperator {

	// MOST BASIC:
	BRACKETS(0, "(", "", ")", "in brackets", 1, 1),
	TIMES(1, "", "*", "", "times", 2, 2),
	BY(2, "", "/", "", "by", 2, 2),
	PLUS(3, "", "+", "", "plus", 2, 3),
	MINUS(4, "", "-", "", "minus", 2, 3),
	DOT(5, "", "dot", "", "dot-product", 2, 2.5),
	POW(6, "", "^", "", "to the power of", 2, 1),
	ABS(7, "abs", "", "", "absolute of", 1, 1),
	DET(8, "det", "", "", "determinant (vector dot product with itself)", 1, 1),
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
	ANGLE(37, "angle", "", "", "angle of", 1, 1),
	LENGTH(38, "length", "", "", "length of", 1, 1),
	EULER_ANGLE(39, "eulerangle", "", "", "eulerian angle of", 1, 1),
	EULER_LENGTH(40, "eulerlength", "", "", "eulerian length of", 1, 1),
	CONJUGATE(41, "conjugate", "", "", "(hyper-)complex conjugate", 1, 1),
	INVERSE(42, "inverse", "", "", "inverse", 1, 1),
	R0(43, "normalized", "", "", "normalized (hyper-)complex vector", 1, 1),
	RE(44, "RE", "", "", "real part (hyper-)complex number", 1, 1),
	IM(45, "IM", "", "", "imaginary part (hyper-)complex number", 1, 1),
	MIRRORED_RADIAL_TO(46, "", "mirrored radial to", "", "mirrored radially to", 2, 1.5),
	MIRRORED_ORTHOGONAL_TO(47, "", "mirrored orthogonal to", "", "mirrored orthogonally to", 2, 1.5),
	PART_RADIAL_TO(48, "", "part towards", "", "part radial to", 2, 1.5),
	PART_ORTHOGONAL_TO(49, "", "part orthogonal to", "", "part orthogonal to", 2, 1.5),
	INT(50, "round", "", "", "rounded real part of", 1, 0.5),
	CEIL(51, "ceil", "", "", "ceiled real part of", 1, 0.5),
	FLOOR(52, "floor", "", "", "floored real part of", 1, 0.5),
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
	
	private SimpleOperator(int code, String symbolLeft, String symbolMiddle, String symbolRight, String command, int involvedTerms, double rank) {
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
