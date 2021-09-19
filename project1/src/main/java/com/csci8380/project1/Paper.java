package com.csci8380.project1;

/**
 * Model representing a published paper.
 */
public class Paper {
    /// Full name of the paper.
    private String name;
    /// Year the paper was published.
    private int year;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getYear() {
        return year;
    }

    public void setYear(int year) {
        this.year = year;
    }
}
