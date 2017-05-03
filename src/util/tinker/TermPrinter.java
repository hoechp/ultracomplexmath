package util.tinker;

import java.util.ArrayList;
import java.util.HashSet;

import util.kd.terms.Property;
import util.kd.terms.TermDeduction;
import util.kd.terms.Thing;
import util.kd.terms.Things;

public class TermPrinter {
	
	public static void main(String[] args) {
		
		/*
		Things t = new Things(4, 1, 200, 0.33);
		TermDeduction d = new TermDeduction(t, 0.01);
		System.out.println(d.getTerms());
		*/
		
		HashSet<Thing> things = new HashSet<Thing>();
		ArrayList<Property> properties = new ArrayList<Property>();
		properties.add(new Property("even", 0));
		properties.add(new Property("odd", 1));
		properties.add(new Property("prime", 2));
		properties.add(new Property("!prime", 3));
		properties.add(new Property("square", 4));
		properties.add(new Property("!square", 5));
		int iMax = 1000;
		for (int i = 1; i <= iMax; ++i) {
			HashSet<Property> currentProperties = new HashSet<Property>();
			currentProperties.add(properties.get(2));
			if (i % 2 == 0) {
				currentProperties.add(properties.get(0));
				if (i != 2) {
					currentProperties.remove(properties.get(2));
				}
			}
			if (i != 1) {
				for (int j = 3; j <= Math.sqrt(iMax); j += 2) {
					if (i % j == 0) {
						currentProperties.remove(properties.get(2));
						break;
					}
				}
			} else {
				currentProperties.remove(properties.get(2));
			}
			for (int j = 1; j <= Math.sqrt(iMax); ++j) {
				if (j * j == i) {
					currentProperties.add(properties.get(4));
					break;
				}
			}
			// invert every second property
			for (int j = 0; j < properties.size() / 2; ++j) {
				if (!currentProperties.contains(properties.get(2 * j))) {
					currentProperties.add(properties.get(2 * j + 1));
				}
			}
			Thing element = new Thing(currentProperties);
			things.add(element);
		}
		System.out.println("numbers 1 to " + iMax + " with properties prime (or not) and even (or not):");
		Things t = new Things(things);
		TermDeduction d = new TermDeduction(t);
		System.out.println("WAY BEFORE: " + d.getTerms());
		d.termReduction(1, true);
		System.out.println("BEFORE: " + d.getTerms());
		d = new TermDeduction(t);
		d.termReduction(0.99, true);
		System.out.println("AFTER: " + d.getTerms());
		
	}
		

}
