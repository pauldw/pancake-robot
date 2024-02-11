# TODO

Running list of possible improvements.

## Control
- Lock axis set (i.e. clamp any of x,y,z,roll,pitch,yaw to 0)

## Recording
- Add sequence stepping
- Add cursor position parameter changes
- Add inserts
- Add deletes
- Add TCP payload changes
- Add TCP offset changes? (problematic as that context is lost in the recorded position)
- Add reference frame changes?
- Add reference frame measurement? (i.e. move robot arm to a certain location and record that as the reference frame)
- Add comment/label ability?

## Pancakes 
- Fix issue where ladle occasionally slides out to the side.
  - Try tipping the ladle more slowly so the batter comes out and reduces weight.
  - Try adding a squish rubber end.
  - Try shortening ladle arm.
- Apply more butter.
- Fix ladle in its location with more certainty (try fixing the measuring cup with a ring at the base, first)
- Tip batter more into the center of the iron.
- Push pancake directly towards the bowl (slightly at an angle).
- Have an infinite loop mode so you don't have to remember to start the next pancake (pancakes should just appear).  Also consider "autonomation" where the robot lets you know the batter is empty.
- Consider adding a "pancake chute", possibly combined with raising the iron so the pancake slides down the chute.
- Add some indicator of the passage of time
  - Have the robot rotate around occasionally.
  - "Have you tried the hot fudge sunday?"
  - Have the robot start a 2 minute countdown timer
- Spatula start scooping (after pushing) closer to edge so the pancake edge isn't squished.