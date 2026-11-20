-- F10 prints the Java bridge status and command help.
local function api()
    if PZMapStudioAPI then
        return PZMapStudioAPI.getInstance()
    end
    return nil
end

local function showHelp()
    local a = api()
    if not a then
        print("[PZMapStudio] Java API not loaded. Approve PZMapStudio.jar in ZombieBuddy if asked.")
        return
    end
    print("[PZMapStudio] " .. a:status())
    print("[PZMapStudio] " .. a:help())
end

local function onKeyPressed(key)
    if key == Keyboard.KEY_F10 then
        showHelp()
    end
end

Events.OnGameStart.Add(showHelp)
Events.OnKeyPressed.Add(onKeyPressed)
