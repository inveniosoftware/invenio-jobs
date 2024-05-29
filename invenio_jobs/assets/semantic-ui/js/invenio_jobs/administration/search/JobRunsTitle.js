export async function JobRunsTitle(pidValue) {
  fetch("/api/jobs/" + pidValue)
    .then((response) => response.json())
    .then((data) => {
      if (data.title) {
        const titleElem = document.getElementsByTagName("h1")[0];
        if (titleElem) {
          titleElem.innerText = data.title;
          const descriptionElem = document.getElementById("description");
          if (descriptionElem && data.description) {
            descriptionElem.innerText = data.description;
          }
        }
      }
    });
}
