package util.kd.terms;

import java.util.ArrayList;
import java.util.HashSet;

import util.basics.Sets;
import util.kd.rules.DataSet;
import util.kd.rules.Rule;
import util.kd.rules.RuleDeduction;

public class TermDeduction {

	/**
	 * Begriffe aus 'binären Werten' ableiten (-> Ankreuzlisten)
	 * Datenstruktur aus Begriffen und Unter-/Oberbegriffen bilden
	 * Werte analog zu Support berechnen, ect...
	 * (...)
	 */

	private Things t;
	private HashSet<Term> terms;
	private double termMinSupp;
	
	public TermDeduction(Things t) {
		this(t, 0);
	}
	
	public TermDeduction(Things t, double minSupp) {
		this.termMinSupp = minSupp;
		this.t = t;
		terms = termDeduction();
	}
	
	public HashSet<Term> termDeduction() {
		// Apriori Begriffsbildung
		HashSet<Term> result = new HashSet<Term>();
		HashSet<Term> step = new HashSet<Term>();
		HashSet<Term> step0 = step;
		for (Property e: t.getUsedProperties()) {
			step.add(new Term(t, e));
		}
		do {
			HashSet<Term> toRemove = new HashSet<Term>();
			for (Term b: step) {
				if (b.supp() <= termMinSupp) {
					toRemove.add(b);
				}
			}
			step.removeAll(toRemove);
			result.addAll(step);
			HashSet<Term> nextStep = new HashSet<Term>();
			for (Term b: step) {
				for (Term b0: step0) {
					Property e = null;
					for (Property e0: b0.getDefinition()) {
						e = e0;
						break;
					}
					if (!b.getDefinition().contains(e)) {
						Term newTerm = new Term(b, b0);
						boolean doesExist = false;
						for (Term b2: nextStep) {
							if (newTerm.getDefinition().containsAll(b2.getDefinition())
									&& b2.getDefinition().containsAll(newTerm.getDefinition())) {
								doesExist = true;
								break;
							}
						}
						if (!doesExist) {
							nextStep.add(newTerm);
						} else {
							newTerm.didntExist();
						}
					}
				}
			}
			step = nextStep;
		} while (step.size() > 0);
		return result;
	}
	
	public void eliminate() {
		HashSet<Term> toRemove = new HashSet<Term>();
		for (Term b: terms) {
			if (b.supp() <= termMinSupp) {
				toRemove.add(b);
			}
		}
		terms.removeAll(toRemove);
	}
	
	public void termReduction() {
		termReduction(1, false);
	}
	
	public void termReduction(double minConf) {
		termReduction(minConf, 0, false);
	}
	
	public void termReduction(double minConf, boolean debug) {
		termReduction(minConf, 0, debug);
	}
	
	public void termReduction(double minConf, double minSupp) {
		termReduction(minConf, minSupp, false);
	}
	
	public void termReduction(double minConf, double minSupp, boolean debug) {
		// if a rule T1 => T2 has conf >= minConf and supp >= minSupp (use util.kd.rules.TermDeduction), apply rule by
		//  - apply 'T1 is a T2'-relationship: T1 is specializedTerm of more general term T2
		//
		// like "prime => odd has 99%" -> apply "prime is odd": prime is specialized from odd
		// => since this is a 'soft' 'is-a'-relationship: add 'odd' to definition of 'prime' => throw 2 out of prime
		RuleDeduction rd = new RuleDeduction(t.toData(), termMinSupp, minConf, minSupp);
		HashSet<Rule> rulesToApply = rd.getRules();
		ArrayList<Term> rulesA = new ArrayList<Term>();
		ArrayList<Term> rulesB = new ArrayList<Term>();
		ArrayList<String> rules = new ArrayList<String>();
		rules = new ArrayList<String>();
		for (Rule r: rulesToApply) {
			rulesA.add(findTerm(r.getA()));
			rulesB.add(findTerm(r.getB()));
			rules.add(rulesA.get(rulesA.size() - 1) + " -> " + rulesB.get(rulesB.size() - 1));
		}
		for (int i = 0; i < rules.size(); ++i) {
			if (rulesA.get(i) == rulesB.get(i)) {
				//System.out.println("ERROR: RULE MAKES NO SENSE)");
				continue;
			}
			Term t1 = rulesA.get(i);
			Term t2 = rulesB.get(i);
			Term tBoth = null; // find term t1 && t2
			for (Term t: terms) {
				HashSet<Property> union = Sets.union(t1.getDefinition(), t2.getDefinition());
				if (t.getDefinition().containsAll(union) && union.containsAll(t.getDefinition())) {
					tBoth = t;
					break;
				}
			}
			// apply rule
			if (tBoth == null) {
				//System.out.println("ERROR: tBoth == null");
			} else if (t1 == null) {
				//System.out.println("ERROR: t1 == null");
			} else if (t1 == tBoth) {
				//System.out.println("ERROR: t1 == tBoth");
			} else {
				if (debug) {
					System.out.println("redefining '" + t1 + "' as '" + tBoth
							+ "' because of rule: '" + rules.get(i) + "'");
				}
				for (int j = 0; j < rules.size(); ++j) {
					if (rulesA.get(j) == tBoth) {
						rulesA.set(j, t1);
					}
					if (rulesB.get(j) == tBoth) {
						rulesB.set(j, t1);
					}
				}
				t1.redefineAs(tBoth);
				terms.remove(tBoth);
			}
		}
		eliminate();
	}

	public Term findTerm(DataSet d) {
		return findTerm(toPropertySet(d));
	}
	
	public Term findTerm(String name) {
		for (Term t: terms) {
			if (name.equals(t.getName())) {
				return t;
			}
		}
		return null;
	}
	
	public HashSet<Property> toPropertySet(DataSet d) {
		HashSet<Property> result= new HashSet<Property>();
		for (int i: d.getDataList()) {
			result.add(t.property(i));
		}
		return result;
	}
	
	public Term findTerm(HashSet<Property> toMatch) {
		for (Term t: terms) {
			if (t.getDefinition().size() != toMatch.size()) {
				continue;
			}
			if (t.getDefinition().containsAll(toMatch) && toMatch.containsAll(t.getDefinition())) {
				return t;
			}
		}
		return null;
	}

	public Things getThings() {
		return t;
	}

	public HashSet<Term> getTerms() {
		return terms;
	}
	
}
