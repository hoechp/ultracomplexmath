package util.basics;

import java.util.HashSet;

public class Sets {
	
	/**
	 * Returns the union of both sets (using HashSet.addAll())
	 * @param a the first set
	 * @param b the second set
	 * @return the union of both sets
	 */
	public static <T> HashSet<T> union(final HashSet<T> a, final HashSet<T> b) {
		HashSet<T> result = new HashSet<T>(a);
		result.addAll(b);
		return result;
	}

	/**
	 * Returns the cut of both sets (using HashSet.retainAll())
	 * @param a the first set
	 * @param b the second set
	 * @return the cut of both sets
	 */
	public static <T> HashSet<T> cut(final HashSet<T> a, final HashSet<T> b) {
		HashSet<T> result = new HashSet<T>(a);
		result.retainAll(b);
		return result;
	}

	/**
	 * Returns set a without set b (using HashSet.removeAll())
	 * @param a the first set
	 * @param b the second set
	 * @return set a without set b
	 */
	public static <T> HashSet<T> without(final HashSet<T> a, final HashSet<T> b) {
		HashSet<T> result = new HashSet<T>(a);
		result.removeAll(b);
		return result;
	}
	
	/**
	 * Returns true if set a contains any element in set b, otherwise false
	 * @param a the first set
	 * @param b the second set
	 * @return true if set a contains any element in set b, otherwise false
	 */
	public static <T> boolean containsAny(final HashSet<T> a, final HashSet<T> b) {
		// return cut(a, b).size() > 0;
		for (T t: b) {
			if (a.contains(t)) {
				return true;
			}
		}
		return false;
	}

}
