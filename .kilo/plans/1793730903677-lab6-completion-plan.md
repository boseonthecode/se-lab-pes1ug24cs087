# Lab 6 Git Commit Plan

## Objective
Commit the required Lab 6 deliverables to the repository.

## Files to Commit
The following files exist in `/home/chthonic/repos/se-lab-pes1ug24cs087/lab6/` and need to be committed:

1. `LAB6_PDF_Report.pdf` - PDF report (user created)
2. `LAB6_REPORT.md` - Markdown report (user created)
3. `final_code_coverage_report.txt` - Code coverage report (95%)
4. `final_branch_coverage_report.txt` - Branch coverage report (100%)
5. `final_code_test_output.txt` - Code test execution output
6. `final_branch_test_output.txt` - Branch test execution output
7. `s1.png` - Screenshot 1
8. `s2.png` - Screenshot 2
9. `.gitignore` - Git ignore configuration (excludes nested repository)

## Commands to Execute

```bash
cd /home/chthonic/repos/se-lab-pes1ug24cs087/lab6

# Add all deliverable files
git add LAB6_PDF_Report.pdf LAB6_REPORT.md final_code_coverage_report.txt final_branch_coverage_report.txt final_code_test_output.txt final_branch_test_output.txt s1.png s2.png .gitignore

# Commit with descriptive message
git commit -m "Add Lab 6 deliverables: coverage reports, test outputs, screenshots, and documentation"
```

## Verification
After committing, run:
```bash
git status
git log --oneline
```

## Expected Outcome
- All deliverable files committed to the repository
- Git log shows the new commit with all files
- Repository is ready for submission