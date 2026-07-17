import "@testing-library/jest-dom";

// jsdom doesn't implement scrollTo on elements — polyfill it so components
// using smooth-scroll behavior (e.g. chat autoscroll) don't crash in tests.
if (typeof Element !== "undefined" && !Element.prototype.scrollTo) {
  Element.prototype.scrollTo = function () {};
}