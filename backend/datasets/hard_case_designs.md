# Hard Evaluation Case Designs

These cases are designs for the next labeled benchmark expansion. They must be backed by retrieved public sources and manually reviewed ground truth before inclusion in the measured comparison.

## Shared-domain collision

Two non-famous people share a name, city, generic software occupation, and employer domain. Their profile pages have different handles, employers, or employment dates and no explicit cross-link. Ground truth: uncertain; a merge is a false merge. This tests whether surface similarity is incorrectly treated as identity evidence.

## Look-alike professional profiles

Two people with the same name and the same occupation appear on separate professional platforms. One has a matching username across platforms; the other has only a similar display name. Ground truth: link only the matching-identifier person; leave the other uncertain. This tests whether the baseline merges all similar profiles while the agent requires identity anchors.

## Temporal and conflicting claims

One person has sequential employers with non-overlapping dates. A separate person has the same name and a conflicting single-valued location or employer during the same period. Ground truth: sequential claims are consistent for the first person; the second person must not be merged. This tests temporal reasoning and contradiction handling together.

Each case should include source URLs, retrieval artifacts, observations, expected verdict, and a short reviewer rationale. The baseline and agent must consume the same saved observations.
