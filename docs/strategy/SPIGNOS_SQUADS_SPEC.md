# SPIGNOS Squads Spec

## Purpose
Private groups for comparing training activity and motivation.
No feed, no comments, no public discovery.

## Data Model
- Squad: name (unique), owner_id
- SquadMembership: squad_id, user_id, role (owner/member)
- SquadInviteCode: code (SPGN-XXXX), expires 48h, single-use

## Invitation Flow
1. Owner generates code on squad detail page
2. Shares code via external channel (message, in-person)
3. Invitee enters code on /squads/join
4. Membership created, code marked as used

## Scoped Leaderboard
Same scoring as global leaderboard but filtered to squad members.
Shows: rank, username, score, sessions, grade, streak, last activity.

## Privacy
See SPIGNOS_SQUADS_PRIVACY_MODEL.md
