package util.tinker;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Random;

import util.ds.BigInt;

public class DS2Tinker {
	
	public static void main(String[] args) {
		
		// DSII-Aufgabe 1 Blatt 9: (WS12/13)
		System.out.println("DSII-Aufgabe 1 Blatt 9: (WS12/13)");
		BigInteger n = new BigInteger("8383");
		ArrayList<BigInteger> output = BigInt.fermatFactors(n);
		System.out.println("n = " + n + " = " + output.get(0) + " * " + output.get(1)
				+ " -> phi = (" + output.get(0) + " - 1) * (" + output.get(1) + " - 1) = "
				+ output.get(0).subtract(BigInteger.ONE).multiply(output.get(1).subtract(BigInteger.ONE)));
		BigInteger e = new BigInteger("3");
		BigInteger d = BigInt.getRSADecoder(n, e);
		System.out.println("n = " + n + ", e = " + e + " is hacked to d = " + d);
		BigInteger c = new BigInteger("313");
		BigInteger m = BigInt.decryptRSA(n, d, c);
		System.out.println("c = " + c + " is decrypted to m = " + m);

		System.out.println();
		// DSII-Aufgabe 2 Blatt 9: (WS12/13)
		System.out.println("DSII-Aufgabe 2 Blatt 9: (WS12/13)");
		n = new BigInteger("1606938044258990275551518141370982378356229797292067198570519");
		output = BigInt.fermatFactors(n, true);
		System.out.println(n + " = " + output.get(1) + " * " + output.get(2));

		System.out.println();
		// DSII-Aufgabe 3 Blatt 9: (WS12/13)
		System.out.println("DSII-Aufgabe 3 Blatt 9: (WS12/13)");
		BigInteger p = new BigInteger(300, 30, new Random());
		BigInteger qMin = new BigInteger(500, 30, new Random());
		BigInteger q = new BigInteger("4");
		BigInteger i = new BigInteger("0");
		BigInteger two = new BigInteger("2");
		if (p.isProbablePrime(30)) {
			System.out.println("p = " + p + " (300 bit prime)");
		}
		while (q.compareTo(qMin) < 0 && !q.isProbablePrime(30)) {
			i = i.add(two);
			q = p.multiply(i).add(BigInteger.ONE);
		}
		if (q.isProbablePrime(30)) {
			System.out.println("q = " + q + " (500 bit prime)");
		}
		System.out.println(i + " * p + 1" + " = q");
		System.out.println(i + " * " + p + " + 1" + " = " + q);
		
	}

}
