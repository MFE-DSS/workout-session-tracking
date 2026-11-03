// Temporary CI-01 acceptance probe; removed before the final delivery HEAD.
test('CI-01 deliberate Jest failure must produce a failing command', () => {
  expect(1).toBe(2);
});
