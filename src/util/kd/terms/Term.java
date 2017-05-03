package util.kd.terms;

import java.util.HashSet;

import util.basics.Sets;

public class Term {
	
	private Things data;

	private HashSet<Term> generalizedTerms;
	private HashSet<Term> specializedTerms;
	
	private String name;

	private HashSet<Property> definition;
	private HashSet<Thing> things;
	
	public String getName() {
		return name;
	}

	public HashSet<Term> getGeneralizedTerms() {
		return generalizedTerms;
	}
	
	public HashSet<Term> getAllGeneralizedTerms() {
		HashSet<Term> result = new HashSet<Term>();
		for (Term t: generalizedTerms) {
			result.add(t);
			result.addAll(t.getAllGeneralizedTerms());
		}
		return result;
	}

	public HashSet<Term> getSpecializedTerms() {
		return specializedTerms;
	}
	
	public HashSet<Term> getAllSpecializedTerms() {
		HashSet<Term> result = new HashSet<Term>();
		for (Term t: specializedTerms) {
			result.add(t);
			result.addAll(t.getAllSpecializedTerms());
		}
		return result;
	}

	public HashSet<Property> getDefinition() {
		return definition;
	}

	public HashSet<Thing> getThings() {
		return things;
	}

	/**
	 * Atomarer Begriff
	 * @param data
	 * @param e
	 */
	public Term(Things data, Property e) {
		this.name = e.toString();
		this.data = data;
		generalizedTerms = new HashSet<Term>();
		specializedTerms = new HashSet<Term>();
		definition = new HashSet<Property>();
		definition.add(e);
		things = new HashSet<Thing>();
		for (Thing g: data.getThings()) {
			if (g.getProperties().contains(e)) {
				things.add(g);
			}
		}
	}
	
	public Term(Term oA, Term oB) {
		this(oA, oB, null);
	}

	/**
	 * Unterbegriffsbildung
	 * @param oA
	 * @param oB
	 */
	public Term(Term oA, Term oB, String name) {
		if (name == null) {
			this.name = oA.name + " && " + oB.name;
		} else {
			this.name = name;
		}
		this.data = oA.data;
		definition = Sets.union(oA.definition, oB.definition);
		things = Sets.cut(oA.things, oB.things);
		generalizedTerms = new HashSet<Term>();
		generalizedTerms.add(oA);
		generalizedTerms.add(oB);
		specializedTerms = new HashSet<Term>();
		oA.specializedTerms.add(this);
		oB.specializedTerms.add(this);
	}
	
	public double supp() {
		return (double)things.size() / (double)data.getThings().size();
	}
	
	public void redefineAs(Term other) {
		adoptProperties(other);
		generalizedTerms.addAll(other.generalizedTerms);
		for (Term t: other.generalizedTerms) {
			t.specializedTerms.remove(other);
			t.specializedTerms.add(this);
		}
		generalizedTerms.remove(this);
		specializedTerms.addAll(other.specializedTerms);
		for (Term t: other.specializedTerms) {
			t.generalizedTerms.remove(other);
			t.generalizedTerms.add(this);
		}
		specializedTerms.remove(this);
		HashSet<Term> toUpdate = Sets.without(getAllSpecializedTerms(), other.getAllSpecializedTerms());
		for (Term t: toUpdate) {
			t.adoptProperties(this);
		}
		other.didntExist();
	}
	
	public void adoptProperties(Term other) {
		definition = Sets.union(definition, other.definition);
		things = Sets.cut(things, other.things);
	}

	public void didntExist() {
		this.name = null;
		for (Term t: generalizedTerms) {
			t.specializedTerms.remove(this);
		}
		for (Term t: specializedTerms) {
			t.generalizedTerms.remove(this);
		}
		specializedTerms = new HashSet<Term>();
		generalizedTerms = new HashSet<Term>();
		definition = new HashSet<Property>();
		things = new HashSet<Thing>();
	}
	
	public String toString() {
		if (name == null) {
			return toString(0);
		} else {
			return name;
		}
	}
	
	/**
	 * if dir > 0 it also prints its more general terms<br>
	 * if dir < 0 it also prints its more specialized terms<br>
	 * if dir == 0 it prints just the term itself<br>
	 * @param dir the direction to follow the term hierarchy
	 * @return a string representation
	 */
	public String toString(int dir) {
		boolean go;
		boolean up = true;
		if (dir == 0) {
			go = false;
		} else if (dir > 0) {
			go = true;
		} else {
			go = true;
			up = false;
		}
		String result = "t_" + definition.toString();
		if (go) {
			if (generalizedTerms.size() > 0 && up) {
				result = result + "_from[";
				boolean first = true;
				for (Term t: generalizedTerms) {
					if (!first) {
						result = result + ", " + t;
					} else {
						result = result + t;
						first = false;
					}
				}
				result = result + "]";
			}
			if (specializedTerms.size() > 0 && !up) {
				result = result + "_derives[";
				boolean first = true;
				for (Term t: specializedTerms) {
					if (!first) {
						result = result + ", " + t;
					} else {
						result = result + t;
						first = false;
					}
				}
				result = result + "]";
			}
		}
		return result;
	}

}
