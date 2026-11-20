# Product and design principles

Scope: the project and all its modules. Status: current.

## P-INPUT: Preserve the intent of the input

Invalid input has to fail explicitly. When a title exceeds the limit, it is not silently truncated; the caller decides how to tell the user.

## P-SCOPE: Keep to the scope of the first version

The title module is responsible only for normalizing and validating strings and does not depend on storage or a user interface. When the responsibilities need to be widened, revise the requirements and the design first.

## P-EVIDENCE: Verification claims have a basis

When recording test results, state the object verified, the command, and the result. An expectation in a plan does not serve as proof that something is done.
