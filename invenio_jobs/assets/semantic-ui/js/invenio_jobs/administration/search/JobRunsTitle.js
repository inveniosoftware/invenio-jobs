export async function JobRunsTitle(pidValue) {
  fetch("/api/jobs/" + pidValue)
    .then((response) => response.json())
    .then((data) => {
      const titleElem = document.getElementsByTagName("h1")[0];
      if (titleElem && data) {
        titleElem.innerHTML = data.title;
        if (data.description) {
          titleElem.classList.add("m-0");
          const description = document.createElement("p");
          description.innerText = data.description;
          description.classList = "ui grey header";
          titleElem.insertAdjacentElement("afterend", description);
        }
      }
    });
}
