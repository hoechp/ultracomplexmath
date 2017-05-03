package util.tests;


import org.junit.Test;

import util.hypercomplex.ultracomplex.Ultra;

public class UltraPerformanceTest {

	static long start = 0;
	static long end = 0;
	static int TESTS = 10;

	@Test
	public void testPerformance() {

		Ultra a = new Ultra(2, 3, 5, 7, 11, 13, 17, 19);
		Ultra b = new Ultra(3, 5, 7, 11, 13, 17, 19, 2);
		Ultra c = new Ultra(5, 7, 11, 13, 17, 19, 2, 3);

		System.out.print("a.plus(b): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.plus(b);
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.minus(b): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.minus(b);
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.times(b): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.times(b);
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.by(b): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.by(b);
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.exp(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.exp();
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.ln(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.ln();
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.pow(b): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.pow(b);
		}
		end();
		System.out.println(" ms / operation ");

		System.out.print("a.sin(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.sin();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.cos(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.cos();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.tan(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.tan();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.cot(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.cot();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.sec(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.sec();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.csc(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.csc();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.sinh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.sinh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.cosh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.cosh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.tanh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.tanh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.coth(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.coth();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.sech(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.sech();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.csch(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.csch();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.asin(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.asin();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acos(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acos();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.atan(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.atan();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acot(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acot();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.asec(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.asec();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acsc(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acsc();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.asinh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.asinh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acosh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acosh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.atanh(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.atanh();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acoth(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acoth();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.asech(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.asech();
		}
		end();
		System.out.println(" ms / operation ");
		System.out.print("a.acsch(): ");
		start();
		for (int i = 0; i < TESTS; ++i) {
			a.acsch();
		}
		end();
		System.out.println(" ms / operation ");

		
	}

	void start() {
		start = System.currentTimeMillis();
	}
	
	void end() {
		end = System.currentTimeMillis();
		System.out.print((double)(end - start) / TESTS);
	}

}
