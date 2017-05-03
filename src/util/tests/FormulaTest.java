package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.calculation.Calculation;
import util.hypercomplex.formula.Formula;
import util.hypercomplex.formula.FormulaSystem;
import util.hypercomplex.formula.Parameter;
import util.hypercomplex.ultracomplex.Ultra;

public class FormulaTest {

	@Test
	public void testFormula() {
		Parameter x = new Parameter("x", new Ultra(3));
		Parameter y = new Parameter("y", new Formula("sqrt(-1)+2+sin(?)", "phi"));
		Ultra xH = new Ultra(3);
		Ultra yH = new Ultra(0, 0, 1, 0, 0, 0, 0, 0).plus(new Ultra(2).plus(Ultra.ZERO.sin()));
		Formula test = new Formula("1+cos(?)*?^?", x, y, x);
		Ultra res = new Ultra(1).plus(xH.cos().times(yH.pow(xH)));
//		Assert.assertEquals(res, test.result());
		test = new Formula("1+cos(psi)*phi^psi");
		test.set("psi", "3");
		test.set("phi", "sqrt(-1)+2+sin(0)");
//		Assert.assertEquals(res, test.result());
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			double range = 5e6;
			Ultra rand = new Ultra(Math.random() * range - range / 2, 0,
					Math.random() * range - range / 2, 0, 0, 0, 0, 0);
			rand = new Ultra(Hypercomplex.parseHypercomplexWeak(rand.toString()));
			Ultra parsed = new Ultra(Hypercomplex.parseHypercomplexWeak(rand.toString()));
			Assert.assertTrue(Tests.compareValue(rand.getDouble(0), parsed.getDouble(0)));
			Assert.assertTrue(Tests.compareValue(rand.getDouble(2), parsed.getDouble(2)));
		}
		Assert.assertEquals(8d, new Formula("2³").result().getDouble(0));
		Formula f = new Formula("x²"); // Parameter x is auto-generated!
		f.set("x", "2²");
		Assert.assertEquals(16d, f.result().getDouble(0));
		Formula g = new Formula("sqrt(y)");
		g.set("y", f);
//		Assert.assertEquals(4d, g.result().getDouble(0));
		f.set("x", 2);
		Assert.assertEquals(2d, g.result().getDouble(0));
		Formula pol = new Formula("x² - x - 1");
		Formula pqNeg = new Formula("-(p/2) - sqrt((p/2)^2 - q)");
		Formula pqPos = new Formula("-(p/2) + sqrt((p/2)^2 - q)");
		pqNeg.set("p", "-1");
		pqNeg.set("q", "-1");
		pqPos.set("p", "-1");
		pqPos.set("q", "-1");
		pol.set("x", pqNeg);
//		Assert.assertTrue(Tests.compareValue(0, pol.result().getDouble(0), 1e5));
		pol.set("x", pqPos); // Goldener Schnitt == max(solve(x, x² -x -1 == 0))
//		Assert.assertTrue(Tests.compareValue(0, pol.result().getDouble(0), 1e5));
		Assert.assertEquals(-1d, new Formula("î²").result().getDouble(0));
		Assert.assertEquals(0d, new Formula("ê²").result().getDouble(0));
		Assert.assertEquals(1d, new Formula("Ê²").result().getDouble(0));
		Assert.assertTrue(Tests.compareValue(-2d, new Formula("-1 - 1").result().getDouble(0), 1e5));
		Assert.assertTrue(Tests.compareValue(0d, new Formula("-1 + 1").result().getDouble(0), 1e5));
		Assert.assertTrue(Tests.compareValue(1d/4d, new Formula("1/2/2").result().getDouble(0), 1e5));
		Assert.assertTrue(Tests.compareValue(Math.E, new Formula("e").result().getDouble(0), 1e5));
		Assert.assertTrue(new Binary(0, -1).equals(Hypercomplex.parseHypercomplexWeak("cos(pi)*Ê")));
		Assert.assertTrue(new Complex(1, 2).equals(Hypercomplex.parseHypercomplexWeak("1 + 1+1î")));
		Assert.assertTrue(new Complex(2, 1).equals(Hypercomplex.parseHypercomplex("1 + 1+1î")));
		Assert.assertTrue(new Complex(0, 1).equals(Hypercomplex.parseHypercomplex("sqrt(-1)")));
		Assert.assertTrue(new Complex(-1).equals(Hypercomplex.parseHypercomplex("sqrt(-1)*î")));
		Assert.assertTrue(new Complex(2500, 2500).equals(
				Hypercomplex.parseHypercomplex("2.5*10^3 * e^(1/4*pi*î) * sqrt(2)")
		));
		Formula f2 = new Formula("(2.5*10^(3 + x) * ((2.5*(2.5*10^(3 + x) * (e + y)^(1/4*pi*(î + z)) " +
				"* sqrt((2.5*10^(3 + x) * (e + (2.5*10^(3 + x) * (e + y)^(1/4*pi*(î + z)) " +
				"* sqrt(2)))^(1/4*pi*(î + z)) * sqrt(2))))^(3 + x) * (e + y)^(1/4*pi*(î + z)) " +
				"* sqrt(2)) + y)^(1/4*pi*(î + z)) * sqrt(2))");
		Assert.assertNotNull(f2.result());

		Ultra c1 = new Ultra(Math.cos(Math.PI / 4) * Math.sqrt(2), 0, Math.sin(Math.PI / 4) * Math.sqrt(2), 0, 0, 0, 0, 0);
		Ultra c2 = new Ultra(2);
		Formula hilbert = new Formula("direction * (vector dot direction) / (direction dot direction)");
		hilbert.set("vector", c1);
		hilbert.set("direction", c2);
//		Assert.assertTrue(hilbert.result().equals(1));
		// and here a demonstration about 'user-created functions'
		Formula modulo = new Formula("arg1 - floor(arg1 / arg2) * arg2");
		Formula formula = new Formula("mod1 + mod2");
		Formula modulo1 = new Formula(modulo);
		formula.set("mod1", modulo1);
		modulo1.set("arg1", 12); // a
		modulo1.set("arg2", 5); // b
		Formula modulo2 = new Formula(modulo);
		formula.set("mod2", modulo2);
		modulo2.set("arg1", 12); // c
		modulo2.set("arg2", 7); // d
//		Assert.assertTrue(formula.result().equals(7)); // 12 % 5 + 12 % 7 == 2 + 5 == 7
		// having added some other parsing features, a little test about Hypercomplex.parseDouble()
		double parsed = Hypercomplex.parseDouble("sqrt(-1)*î"); // this is a real number
		Assert.assertEquals(-1d, parsed); // -> SUCCESS
		boolean catched = false;
		try {
			parsed = Hypercomplex.parseDouble("sqrt(-1)"); // this is a (complex-)imaginary number
			Assert.assertTrue(false);
		} catch (NumberFormatException n) {
			catched = true;
		}
		Assert.assertTrue(catched); // -> FAIL
		Assert.assertTrue(Tests.compareValue(-8d, Hypercomplex.parseDouble("IM((1 + î)^7)")));
		Assert.assertNotNull(new Formula("cos(pi)*Ê²").result());
		/*
		 * now a performance test that under different workloads showed:
		 * - that Formula is ~100x per depth of Parameters slower than Hypercomplex
		 * - Calculation despite of the Parameter-depth of zero is not much faster
		 * - the only 'fast' computation is done using java-syntax and Hypercomplex
		 * so Formula (and Calculation) is only suitable for user-input.
		 */
		Formula fPerf = new Formula("abs(x^(-2))");
		Formula fPos = new Formula("(3 + 2 * cos(phi / 7)) * e^(phi*î)");
		fPerf.set("x", fPos);
		int c = 1; // increase value to performance-test
		for (int i = 0; i < c; ++i) {
			fPos.get("phi").getFormula().result().set(fPos.get("phi").getFormula().result().plus(Ultra.ONE.by(c/Math.PI/2)));
			Ultra result = fPerf.result();
//			Assert.assertNotNull(result);
			//System.out.println(result);
		}
		fPerf = new Formula("abs(((3 + 2 * cos(x / 7)) * e^(x*î))^(-2))");
		double phi = 0;
		for (int i = 0; i < c; ++i) {
			phi += 1/(c/Math.PI/2);
			fPerf.set("x", phi);
			Ultra result = fPerf.result();
//			Assert.assertNotNull(result);
			//System.out.println(result);
		}
		phi = 0;
		for (int i = 0; i < c; ++i) {
			phi += 1/(c/Math.PI/2);
			Ultra nextValue = new Ultra(new Complex("p", 3 + 2 * Math.cos(phi / 7), phi));
			Ultra result = new Ultra(nextValue.pow(new Ultra(-2)));
			Assert.assertNotNull(result);
			//System.out.println(result);
		}
		phi = 0;
		for (int i = 0; i < c; ++i) {
			phi += 1/(c/Math.PI/2);
			Ultra phiC = new Ultra(phi);
			Ultra result = new Calculation("abs(((3 + 2 * cos(" + phiC + " / 7)) * e^(" + phiC + "*î))^(-2))").result();
//			Assert.assertNotNull(result);
			//System.out.println(result);
		}
		/*
		 * now a quick test for the new class FormulaSystem
		 * - testing different ways of setting up and changing a formula
		 */
//		FormulaSystem formulaSystem = new FormulaSystem("f", "x^2").set("x", "sqrt(y)").set("y", "e^z").set("z", "ln(a)").set("a", "b*c").set("b", "sqrt(-1)").set("c", "(1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("f = x^2").set("x := sqrt(y)", "y = e^z", "z = ln(a)", "a = b*c", "b = sqrt(-1)", "c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("x^2").set("x := sqrt(y)", "y = e^z", "z = ln(a)", "a = b*c", "b = sqrt(-1)", "c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("f = x^2", "x := sqrt(y)", "y = e^z", "z = ln(a)", "a = b*c", "b = sqrt(-1)", "c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("x^2", "x := sqrt(y)", "y = e^z", "z = ln(a)", "a = b*c", "b = sqrt(-1)", "c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("f = x^2, x = sqrt(y), y = e^z, z = ln(a), a = b*c, b = sqrt(-1), c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem = new FormulaSystem("x^2, x = sqrt(y), y = e^z, z = ln(a), a = b*c, b = sqrt(-1), c = (1 + î)²");
//		Assert.assertTrue(Tests.compareValue(-2, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem.set("y = 5");
//		Assert.assertTrue(Tests.compareValue(5, formulaSystem.result().getDouble(0), 1e2));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2), 1e2));
//		formulaSystem.set("formula = 3");
//		Assert.assertTrue(Tests.compareValue(3, formulaSystem.result().getDouble(0)));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2)));
//		Assert.assertTrue(Tests.compareValue(3, formulaSystem.get("formula").result().getDouble(0)));
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.get("formula").result().getDouble(2)));
//		formulaSystem = new FormulaSystem("-(p / 2) + sqrt((p / 2)² - q), p = -1, q = -1");
//		Assert.assertTrue(Tests.compareValue((1 + Math.sqrt(5)) / 2, formulaSystem.result().getDouble(0)));
//		formulaSystem = new FormulaSystem("-(p / 2) + sqrt((p / 2)² - q), p = -1, q = -1");
//		Assert.assertTrue(Tests.compareValue(0, formulaSystem.result().getDouble(2)));
		
	}
	
}
