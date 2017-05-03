package util.tests;

import java.math.BigInteger;
import java.util.ArrayList;

import junit.framework.Assert;
import org.junit.Test;

import util.ds.BigInt;

public class BigIntTest {

	@Test
	public void testBigInt() {
		// DSII-Aufgabe 1 Blatt 9: (letzes mal)
		// DSII-Aufgabe 2 Blatt 9: (WS12/13) <- ja, die selben zahlen wie letzes mal...
		BigInteger n = new BigInteger("1606938044258990275551518141370982378356229797292067198570519");
		BigInt num1 = new BigInt("1267650600228229401499935529979");
		BigInt num2 = new BigInt("1267650600228229401501009274261");
		ArrayList<BigInteger> output = BigInt.fermatFactors(n, true);
		Assert.assertEquals(output.get(0), BigInt.ONE);
		Assert.assertEquals(output.get(1), num1);
		Assert.assertEquals(output.get(2), num2);
		// System.out.println(BigInt.fermatOutput(output));
		
		// test euklid
		ArrayList<BigInteger> euklid = BigInt.euklid(new BigInt("40"), new BigInt("7"));
		num1 = new BigInt("3");
		num2 = new BigInt("-17");
		Assert.assertEquals(euklid.get(0), BigInt.ONE);
		Assert.assertEquals(euklid.get(1), num1);
		Assert.assertEquals(euklid.get(2), new BigInt("40"));
		Assert.assertEquals(euklid.get(3), num2);
		Assert.assertEquals(euklid.get(4), new BigInt("7"));

		euklid = BigInt.euklid(new BigInt("8200"), new BigInt("3"));
		Assert.assertEquals(euklid.get(0), new BigInt("1"));
		Assert.assertEquals(euklid.get(1), new BigInt("1"));
		Assert.assertEquals(euklid.get(2), new BigInt("8200"));
		Assert.assertEquals(euklid.get(3), new BigInt("-2733"));
		Assert.assertEquals(euklid.get(4), new BigInt("3"));
		
		euklid = BigInt.euklid(new BigInt("40"), new BigInt("5"));
		Assert.assertEquals(euklid.get(0), new BigInt("5"));
		Assert.assertEquals(euklid.get(1), new BigInt("1"));
		Assert.assertEquals(euklid.get(2), new BigInt("40"));
		Assert.assertEquals(euklid.get(3), new BigInt("-7"));
		Assert.assertEquals(euklid.get(4), new BigInt("5"));
		
		euklid = BigInt.euklid(new BigInt("40"), new BigInt("15"));
		Assert.assertEquals(euklid.get(0), new BigInt("5"));
		Assert.assertEquals(euklid.get(1), new BigInt("-1"));
		Assert.assertEquals(euklid.get(2), new BigInt("40"));
		Assert.assertEquals(euklid.get(3), new BigInt("3"));
		Assert.assertEquals(euklid.get(4), new BigInt("15"));
		
		// test RSA-stuff
		ArrayList<BigInteger> temp = BigInt.generateRSAData(32, 0);
		BigInteger m = new BigInteger("" + (int)(Math.random() * 1e32)).mod(temp.get(0));
		BigInteger c = BigInt.encryptRSA(temp.get(0), temp.get(1), m);
		Assert.assertEquals(m, BigInt.decryptRSA(temp.get(0), temp.get(5), c));
		Assert.assertEquals(m, BigInt.hackRSA(temp.get(0), temp.get(1), c));
		
	}

}
