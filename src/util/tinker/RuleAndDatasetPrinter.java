package util.tinker;

import java.util.HashSet;

import util.kd.rules.Data;
import util.kd.rules.RuleDeduction;

public class RuleAndDatasetPrinter {
	
	public static void main(String[] args) {
		
		Data d = new Data();
		for (int i = 0; i < 100; ++i) {
			HashSet<Integer> dataPoint = new HashSet<Integer>();
			for (int j = 0; j < 4; ++j) {
				dataPoint.add((int)(Math.random() * 10));
			}
			
			d.addData(dataPoint);
		}
		RuleDeduction rd = new RuleDeduction(d, 0.1, 0.4, 0.5);
		System.out.println(rd.getTotal());
		System.out.println(rd.getItems());
		System.out.println(rd.getRules());
	}
		

}
