<script lang="ts">
  let spotifyLogin: string = "false";
  let spotifyResponse: string = "Log In to Spotify";
  let output = "Nothing";
  let playlists = [];
  let playlistSelected = "None";
  async function fetchPlaylist() {
    try {
      const response = await fetch(`http://localhost:8090/getPlaylists`, { method: 'GET' });
      if (response.ok) {
        const data = await response.json();
        playlists = data.playlists || []; // Default to an empty array
        output = JSON.stringify(data, null, 2);
      } else {
        output = `Error: ${response.status} ${response.statusText}`;
      }
    } catch (error) {
      output = `Fetch failed: ${error.message}`;
    }
  }


  async function youtubeAuth() {
    try {
    window.location.href = 'http://localhost:8090/authorize'; // Redirect the user to the /authorize route
  } catch (error) {
    output = `Fetch failed: ${error.message}`;
  }
  }

  async function spotifyAuth() {
    try {
    window.location.href = 'http://localhost:8090/spotifyLogin'; // Redirect the user to the /authorize route
  } catch (error) {
    output = `Fetch failed: ${error.message}`;
  }
  }
  function spotifyLog() {
    spotifyResponse = "Logged In";
    spotifyLogin = "true";
  }

  async function submitSpotifyPlaylist() {
    if (!spotifyPlaylistLink) {
      output = "Please enter a valid Spotify playlist URL.";
      return;
    }

    try {
      const response = await fetch('http://localhost:8090/spotifyPlaylist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ playlistUrl: spotifyPlaylistLink }),
      });

      if (response.ok) {
        const data = await response.json();
        output = `Playlist processed: ${JSON.stringify(data, null, 2)}`;
      } else {
        output = `Error: ${response.status} ${response.statusText}`;
      }
    } catch (error) {
      output = `Fetch failed: ${error.message}`;
    }
  }

  function handlePlaylistClick(playlist) {
    playlistSelected = playlist;
    console.log(playlistSelected);
  }

  async function submitPlaylist(playlistSelected) {
    console.log(playlistSelected);
    try {
      const response = await fetch('http://localhost:8090/getSongs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ selected: playlistSelected }),
      });

      console.log("response:", response);

      if (response.ok) {
        console.log("before awaiting response works");
      } else {
        console.log("doesnt work");
        output = `Error: ${response.status} ${response.statusText}`;
      }
    } catch (error) {
      console.log("doesnt work pt2");
      output = `Fetch failed: ${error.message}`;
    }
  }

</script>


<main class="flex flex-col justify-between h-screen m-5">
  <div>
    <h1 class="text-center text-3xl md:text-6xl mt-8 text-[#9AFFBA] font-medium">
      Welcome to Playlist Exporter!
    </h1>
    <p class="text-center text-xl md:text-2xl mt-5 text-white mb-6">
      Start Converting Your Playlists from Spotify to YouTube
    </p>
    <div class="flex flex-col items-center space-y-4">

      <div class="flex flex-row gap-3">
        <button  
          class="md:text-2xl text-center text-white bg-green-500 py-2 px-4 rounded hover:bg-green-600"
          on:click={() => {spotifyAuth(), spotifyLog()}}>
          {spotifyResponse}
        </button>
      </div>

      <div class="flex flex-row gap-3">
      
        <button class="md:text-2xl text-center text-black bg-white py-2 px-4 rounded hover:bg-[#9AFFBA] mt-10"
        on:click={() => {fetchPlaylist(), spotifyLog()}}>
          Get Playlists
        </button>

        <p class="md:text-2xl text-center text-white py-2 px-4 mt-10 ">Selected Playlist: {playlistSelected}</p>
      </div>


      {#if spotifyLogin == "true"}
        <button  
          class="md:text-2xl text-center text-white bg-red-500 py-2 px-4 rounded hover:bg-red-600"
          on:click={youtubeAuth}>
          Login with Youtube
        </button>
        {/if}

    <!-- Display Playlists -->
    <div class="space-y-4 w-full text-center">
      {#if playlists.length > 0}
        <ul class="space-y-2 flex flex-wrap justify-center gap-4">
          {#each playlists as playlist}
            <li 
              class="cursor-pointer bg-white hover:bg-gray-300 px-5 py-5 w-64 h-12 rounded flex items-center justify-center"
              on:click={() => handlePlaylistClick(playlist)}>
              {playlist}
            </li>
          {/each}
        </ul>
      {:else}
        <p class="text-gray-500">No playlists available. Please login to fetch playlist</p>
      {/if}
    </div>
    

    
    <button
          on:click={(event) => submitPlaylist(playlistSelected)}
          class="md:text-2xl text-center text-white bg-blue-500 py-2 px-4 rounded hover:bg-blue-600"
        >
          Submit Playlist
      </button>

    <div> 
  </div>
<!--
  <div class="text-center absolute bottom-0">
    <p class="md:text-xl text-[#FFAAAA] mb-4">
      Here is a song recommendation while you login!
    </p>
    <iframe 
      class="w-full sm:w-96 h-24 rounded-lg m-auto" 
      src="https://open.spotify.com/embed/track/52dF752HWIsv2CpSuTX3p2?utm_source=generator" 
      frameborder="0" 
      allowfullscreen 
      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
      loading="lazy" 
      title="Spotify Song Player">
    </iframe>
  </div>

  -->
</main>

<style>
  :global(body) {
    background-color: #181818;
    font-family: "Alegreya Sans", sans-serif;
  }
</style>