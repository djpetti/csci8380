package com.csci8380.project1;

import java.util.ArrayList;
import java.util.List;

/**
 * Model representing the result of a conflict check query.
 */
public class ConflictCheckResult {
    /// Level of conflict-of-interest present.
    private ConflictLevel level;
    /// List of overlapping papers.
    private List<Paper> papers = new ArrayList<>();

    public ConflictLevel getLevel() {
        return level;
    }

    public void setLevel(ConflictLevel level) {
        this.level = level;
    }

    public List<Paper> getPapers() {
        return papers;
    }

    public void setPapers(List<Paper> papers) {
        this.papers = papers;
    }
}
