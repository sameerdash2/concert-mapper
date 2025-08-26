<!-- eslint-disable max-len -->
<template>
  <div class="cell p-4">
    <h2>About</h2>

    <h4>How does this website work?</h4>
    <p>
      The site looks up an artist name in the <a href="https://www.setlist.fm/">setlist.fm</a> API and then retrieves all the setlists for that artist. Setlist.fm is a large community-maintained database of songs played at concerts, known as "setlists."
    </p>

    <h4>Why do pins appear in a circle?</h4>
    <p>The map coordinates returned by setlist.fm identify the city of the concert, rather than the specific venue. This means multiple concerts in the same city would have their pins placed on the same spot. To prevent this, I spread the pins into a circle around the city center, so each one can be clicked.</p>

    <h2>Credits</h2>
    <p>Concert data is retrieved from <a href="https://www.setlist.fm/">setlist.fm</a>.</p>
    <p>Artist images are retrieved from Spotify, when available.</p>
    <p>The source code is available <a href="https://github.com/sameerdash2/concert-mapper">on GitHub</a>.</p>

    <div class="cell has-text-right">
      <RouterLink to="/">
        Home
      </RouterLink>
    </div>
  </div>
</template>
