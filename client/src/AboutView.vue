<!-- eslint-disable max-len -->
<template>
  <div class="cell">
    <h2>About</h2>

    <p>Learn about concert mapper 📍</p>

    <h4>How does this website work?</h4>
    <p>
      The site looks up an artist name in the <a href="https://www.setlist.fm/">setlist.fm</a> API and then retrieves all the setlists for that artist. Setlist.fm is a large community-maintained database of songs played at concerts, known as "setlists."
    </p>

    <h4>Why do pins appear in a circle?</h4>
    <p>Two things to consider:</p>
    <p>The data returned by setlist.fm provides map coordinates for each concert, but these coordinates identify the <strong>city</strong> of the concert, not the specific venue. This means pins will appear on the geographical center of the city, rather than where the concert actually happened. (While it's probably possible to use the venue name to search for more accurate coordinates, that would mean a lot of extra requests and potential errors to handle.)</p>
    <p>This introduces a problem: Multiple concerts in the same city will have their pins overlapped. To prevent this, I "spread" the pins into a circle around the city's center. Sometimes that process pushes pins into the ocean, but at least every pin can be clicked.</p>

    <h2>Credits</h2>
    <p>Concert data is retrieved from <a href="https://www.setlist.fm/">setlist.fm</a>.</p>
    <p>Artist images are retrieved from <a href="https://fanart.tv/">fanart.tv</a>, when available.</p>
    <p>The source code is available <a href="https://github.com/sameerdash2/concert-mapper">on GitHub</a>.</p>
  </div>
  <div class="cell has-text-right">
    <RouterLink to="/">
      Home
    </RouterLink>
  </div>
</template>
