import { RunButton } from "./RunButton";
import React from "react";
import ReactDOM from "react-dom";

export async function JobRunsHeader(pidValue) {
  fetch("/api/jobs/" + pidValue)
    .then((response) => response.json())
    .then((data) => {
      if (data.title) {
        const titleElem = document.getElementById("title");
        if (titleElem) {
          titleElem.innerText = data.title;
          const descriptionElem = document.getElementById("description");
          if (descriptionElem && data.description) {
            descriptionElem.innerText = data.description;
          }
        }
      }

      const actions = document.getElementById("actions");
      ReactDOM.render(<RunButton config={data.default_args} />, actions);
    });
}
