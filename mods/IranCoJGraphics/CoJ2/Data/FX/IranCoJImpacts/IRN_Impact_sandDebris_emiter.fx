EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 5, 9)
	}

	StartVelocity()
	{
		keyf(0, 420)
	}

	StartVelocityRand()
	{
		keyv(0, 240, 220, 240)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_DebrisDirt_trace.fx")
		Probability(1)
	}
}
