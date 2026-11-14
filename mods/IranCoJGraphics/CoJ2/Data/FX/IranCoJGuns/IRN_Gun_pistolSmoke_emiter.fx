EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.9)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 5)
	}

	StartVelocity()
	{
		keyf(0, 800)
	}

	StartVelocityRand()
	{
		keyv(0, 120, 240, 240)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
